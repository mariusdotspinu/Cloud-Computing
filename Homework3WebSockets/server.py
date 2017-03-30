import socketio
import eventlet
import matplotlib.pyplot as plt
import numpy as np
import bs4
import json
import datetime
import urllib
import time

from urllib import request
from flask import Flask, render_template

sio = socketio.Server()
app = Flask(__name__)
app.config.update(TEMPLATE_AUTO_RELOAD=True, DEBUG=True)  # we want to refresh index.html when updated

ERROR_PLOT = "Cannot plot equation !"


# calculate derivate of client's formula using newton API
def get_derive(formula):
    response = urllib.request.urlopen(f"https://newton.now.sh/derive/" + formula)

    my_json_response = json.load(response)

    if "result" in my_json_response:
        return my_json_response["result"]

    return my_json_response["error"]


# write to <body> tag in html file
def update_html(html, sid, derivate, date, img):

    with open(html) as f:
        txt = f.read()
        soup = bs4.BeautifulSoup(txt)

    new_image = soup.new_tag('img', src=img)
    info = " Date : " + date + "     Client : " + sid + \
           " had sent an equation resulting the derive -> " + derivate + " and plot\n"

    br = soup.new_tag('br')

    soup.body.append(info)
    soup.body.append(new_image)
    soup.body.append(br)
    soup.body.append("\n")

    with open(html, "w") as f:
        f.write(str(soup))


# plot equation
def plot_equation(formula, sid):
    formula.replace("^", "**")
    for i in range(0, len(formula)-1):
        if formula[i] == ' ' and formula[i + 1] == "x" or formula[i+1] == "(":
            formula[i] = "*"

    try:
        x = np.array(range(-100, 110))
        y = eval(formula)
        plt.plot(x, y, color=np.random.rand(3, 1))

        current_time = time.time()
        name = "static/" + sid + str(current_time) + ".png"  # static folder , from where flask takes images
        plt.savefig(name)
        plt.clf()  # clear plot to avoid overlaying last plots

        return name

    except Exception:
        return ERROR_PLOT


# Flask web-socket
@app.route('/')
def index():
    """Serve the client-side application."""
    return render_template('index.html')


@sio.on('connect')
def connect(sid, environ):
    print('Client with session id : ', sid + " connected")


@sio.on('equation')
def message(sid, data):
    metric = time.time()
    print('I have received equation: ', data, "from client :", sid)
    print("Creating plot...")
    value = plot_equation(data, sid)

    if value != ERROR_PLOT:
        print("Updating server...")
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        update_html("templates/index.html", sid, get_derive(data), current_time, value)
        print("Updated")
        ok_message = ("Check server, plots updated", time.time())
        sio.emit('update', ok_message, None, None, '/ns')  # tell the client he successfully plotted
        print("Finished in : " + str(time.time() - metric))
    else:
        print(ERROR_PLOT)


@sio.on('disconnect')
def disconnect(sid):
    print('Client with session id :', sid + " disconnected")


if __name__ == '__main__':
    # wrap Flask application with socketio's middleware
    app = socketio.Middleware(sio, app)
    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('127.0.0.1', 3409)), app)

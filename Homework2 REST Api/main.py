import json
import csv
import re

from http.server import BaseHTTPRequestHandler, HTTPServer


def init_data():
    """
    Reads the data from file and puts it into a json
    :return: dictionary based on data from .csv file
    """
    result = {}
    with open("data.csv", 'r') as f:
        data = csv.reader(f, delimiter=',')

        ids = next(data)[1:]
        for row in data:
            temp = {}
            player_id = row[0]
            info = []

            for i in row[1:]:
                info.append(i)

            for i in range(len(info)):
                temp[ids[i]] = info[i]

            result[player_id] = temp

    return json.dumps(result, indent=5)


def is_duplicate_id(m_id):
    """
    Checks if the id given, is already in our dictionary
    :param m_id: id of the tennis player
    :return: True or False
    """
    global m_data
    if m_id in m_data:
        return True
    return False


def verify_data(m_dict):
    """
    Verifies if the given dictionary is properly sent by the client
    :param m_dict: dictionary taken from body (raw) json-type (client)
    :return: message based on dictionary data
    """
    global possible_keys
    for key in m_dict.keys():
        if key not in possible_keys and key != "id":
            return "Not good"

    if "id" in m_dict and "name" in m_dict and "G.S.Tournaments" in m_dict:
        if type(m_dict["id"]) == int and type(m_dict["name"]) == str and type(m_dict["G.S.Tournaments"]) == int and \
                        is_duplicate_id(str(m_dict["id"])) is False:
            return "Ok"
        else:
            return "Duplicate"

    return "Not good"


def insert_to_dict(m_dict):
    """
    Inserts new record in our tennis leader-board, we are also making sure that however our clients pass the data, we
    will keep the same order for our (key,value) pairs for proper iteration.
    :param m_dict: dictionary taken from body (raw) json-type (client)
    """
    global m_data

    # construct ordered new dict
    new_id = str(m_dict["id"])
    name = m_dict["name"]
    gender = "unknown"
    nationality = "unknown"

    # checking optional attributes
    if "gender" in m_dict:
        gender = m_dict["gender"]
    if "nationality" in m_dict:
        nationality = m_dict["nationality"]

    tournaments = m_dict["G.S.Tournaments"]
    del m_dict

    m_dict = {"name": name,
              "gender": gender,
              "nationality": nationality,
              "G.S.Tournaments": tournaments
              }

    m_data[new_id] = m_dict


def update(m_dict, m_id):
    """
    Used for PUT verb, updates the content based on given id
    :param m_dict: dictionary taken from body (raw) json-type (client)
    :param m_id: id given
    :return: message based on dictionary data
    """
    global m_data

    for key in m_dict:
        if key not in possible_keys:
            return "Not good"

    old = m_data[m_id]

    # see if something has changed
    if "name" in m_dict and old["name"] != m_dict["name"]:
        old["name"] = m_dict["name"]

    if "gender" in m_dict and old["gender"] != m_dict["gender"]:
        old["gender"] = m_dict["gender"]

    if "nationality" in m_dict and old["nationality"] != m_dict["nationality"]:
        old["nationality"] = m_dict["nationality"]

    if "G.S.Tournaments" in m_dict and old["G.S.Tournaments"] != m_dict["G.S.Tournaments"]:
        old["G.S.Tournaments"] = m_dict["G.S.Tournaments"]

    m_data[m_id] = old

    return "Ok"


def send_proper_response(self, code):
    """
    Customised function for sending proper response
    :param self: current object
    :param code: Status code to be sent (int)
    """
    self.send_response(code)
    self.send_header('Content-type', 'application/json')
    self.end_headers()


# load leader-board into memory
m_data = json.loads(init_data())

# keys accepted (id is used for the container dictionary)
possible_keys = ["name", "G.S.Tournaments", "gender", "nationality"]


class TennisPlayersRequestHandler(BaseHTTPRequestHandler):
    # GET
    def do_GET(self):

        if None is not re.search("/api/players*", self.path):
            searched_id = self.path.split('/')[-1]

            if str(searched_id).isdigit():

                if self.path.split('/')[-2] != "players":
                    send_proper_response(self, 400)
                    return

                if searched_id in m_data:
                    send_proper_response(self, 200)
                    self.wfile.write(bytes(json.dumps(m_data[searched_id]), "utf-8"))
                else:
                    send_proper_response(self, 400)
                    self.wfile.write(bytes("Player not found!", "utf-8"))

            elif searched_id == "players":
                send_proper_response(self, 200)
                self.wfile.write(bytes(json.dumps(m_data), "utf-8"))
            else:
                send_proper_response(self, 404)
        else:
            send_proper_response(self, 404)
        return

    # POST
    def do_POST(self):
        if self.path == "/api/players":
            length = int(self.headers.get("content-length", 0))
            body = self.rfile.read(length)

            try:
                body = json.loads(body)
            except json.JSONDecodeError:
                send_proper_response(self, 422)
                return

            verification = verify_data(body)

            if verification == "Ok":
                insert_to_dict(body)
                send_proper_response(self, 201)
            elif verification == "Duplicate":
                send_proper_response(self, 409)
            else:
                send_proper_response(self, 400)

        else:
            send_proper_response(self, 404)

        return

    # PUT

    def do_PUT(self):
        if None is not re.search("/api/players*", self.path):
            searched_id = self.path.split('/')[-1]

            if str(searched_id).isdigit():

                if self.path.split('/')[-2] != "players":
                    send_proper_response(self, 400)
                    return

                if searched_id in m_data:

                    length = int(self.headers.get("content-length", 0))
                    body = self.rfile.read(length)

                    try:
                        body = json.loads(body)
                    except json.JSONDecodeError:
                        send_proper_response(self, 422)
                        return

                    update_message = update(body, searched_id)

                    if update_message == "Ok":
                        send_proper_response(self, 200)
                    else:
                        send_proper_response(self, 422)

                else:
                    send_proper_response(self, 400)

            else:
                send_proper_response(self, 404)
        else:
            send_proper_response(self, 404)
        return

    # DELETE

    def do_DELETE(self):
        if None is not re.search("/api/players*", self.path):
            searched_id = self.path.split('/')[-1]

            if str(searched_id).isdigit():

                if self.path.split('/')[-2] != "players":
                    send_proper_response(self, 400)
                    return

                if searched_id in m_data:
                    del(m_data[searched_id])
                    send_proper_response(self, 204)
                else:
                    send_proper_response(self, 400)

            else:
                send_proper_response(self, 404)
        else:
            send_proper_response(self, 404)
        return


def start():
    print("Setting up server...")

    server_address = ('127.0.0.1', 30045)
    httpd = HTTPServer(server_address, TennisPlayersRequestHandler)
    print("Running server...")
    httpd.serve_forever()


start()

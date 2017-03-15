import sys
import urllib
import json

from urllib import request
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QPlainTextEdit, QHBoxLayout, \
    QVBoxLayout, QLabel, QLineEdit, QMessageBox, QTextBrowser
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSlot


# helper functions
def iterate_nested_dict(current_dict, key_desired):
    if len(current_dict) == 0:
        return None
    if isinstance(current_dict, list):
        current_dict = current_dict[0]
    for key, value in current_dict.items():
        if key == key_desired:
            return current_dict[key]
        elif isinstance(value, dict):
            return iterate_nested_dict(value, key_desired)

# open source
the_guardian_api_key = "API-KEY"


# 1 - Database of curated mutations - DoCM API - contains a list of aprox. 163 genes

def get_first_web_service_data(gene):
    response = urllib.request.urlopen\
        (f"http://docm.genome.wustl.edu/api/v1/variants.json?genes={gene}&version=2")

    my_json_response = json.load(response)

    return iterate_nested_dict(my_json_response, 'diseases')


# 2 - Wikipedia - MediaWiki API
def get_second_web_service_data(disease):
    disease = disease.replace(' ', '%20')
    response = urllib.request.\
        urlopen\
        ("https://en.wikipedia.org/w/api.php?format=json"
         f"&action=query&prop=extracts&redirects=1&exintro=&explaintext=&titles={disease}")

    my_json_response = json.load(response)

    return iterate_nested_dict(my_json_response, 'extract')


# 3 - The Guardian - The Guardian Open Platform API

def get_third_web_service_data(disease):
    global the_guardian_api_key
    disease = disease.replace(' ', '%20')

    response = urllib.request.urlopen\
        (f"http://content.guardianapis.com/search?q=\"{disease}\"&format=json&order-by=relevance&api-key="
         f"{the_guardian_api_key}")

    my_json_response = json.load(response)

    return iterate_nested_dict(my_json_response['response']['results'], 'webUrl')


# GUI
class App(QWidget):
    def __init__(self):
        super().__init__()

        self.font = QFont()
        self.title = 'Cloud Computing Homework 1'
        self.left = 50
        self.top = 100
        self.width = 1500
        self.height = 800

        self.font.setPointSize(15)

        self.list_of_diseases = QPlainTextEdit(self)
        self.list_of_diseases.resize(400, 50)

        self.definition_and_articles = QPlainTextEdit(self)
        self.definition_and_articles.resize(400, 50)

        self.web_form = QTextBrowser(self)
        self.web_form.setOpenExternalLinks(True)
        self.web_form.resize(400, 50)

        self.definition_and_articles.setFont(self.font)
        self.definition_and_articles.setReadOnly(True)

        self.list_of_diseases.setFont(self.font)
        self.list_of_diseases.setReadOnly(True)

        self.gene_edit = QLineEdit(self)
        self.gene_edit.setFont(self.font)
        self.web_form.setFont(self.font)

        self.initUI(self.web_form, self.definition_and_articles, self.list_of_diseases, self.font, self.gene_edit)

    def initUI(self, web_form, definition_and_articles, list_of_diseases, font, gene_edit):

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.size())

        label1 = QLabel("Enter gene : (e.g: KRAS/GNA11/TP53/ERBB2/NRAS/KIT...) ")
        label1.setFont(font)

        label2 = QLabel("List of Diseases (DoCM API) : ")
        label2.setFont(font)

        label3 = QLabel("Information (Wikipedia API) : ")
        label3.setFont(font)

        label4 = QLabel("Latest article (The Guardian API) :")
        label4.setFont(self.font)

        button1 = QPushButton('Process', self)
        button1.setFixedHeight(50)
        button1.clicked.connect(self.on_click)

        m_v_box1 = QVBoxLayout()
        m_v_box1.addWidget(label1)
        m_v_box1.addWidget(gene_edit)
        m_v_box1.addWidget(label3)
        m_v_box1.addWidget(definition_and_articles)

        m_v_box2 = QVBoxLayout()
        m_v_box2.addWidget(label2)
        m_v_box2.addWidget(list_of_diseases)

        m_h_box = QHBoxLayout()
        m_h_box.addLayout(m_v_box1)
        m_h_box.addLayout(m_v_box2)

        final_layout = QVBoxLayout()
        final_layout.addLayout(m_h_box)
        final_layout.addWidget(button1)
        final_layout.addWidget(label4)
        final_layout.addWidget(web_form)

        self.setLayout(final_layout)
        self.show()

    @pyqtSlot()
    def on_click(self):
        try:
            self.web_form.clear()
            gene_data = self.gene_edit.text().upper()
            if len(gene_data) == 0:
                raise Exception
            else:
                diseases = get_first_web_service_data(gene_data)
                information = ""
                list_dis = ""

                for i in range(0, len(diseases)):
                    list_dis += diseases[i]

                    if i != len(diseases)-1:
                        list_dis += ", "

                    information += diseases[i] + ":\n\n" + get_second_web_service_data(diseases[i]) + "\n\n"

                self.list_of_diseases.setPlainText("Diseases :\n" + list_dis)
                self.definition_and_articles.setPlainText(information)

                for i in diseases:
                    info = str(get_third_web_service_data(i))
                    self.web_form.append(f"<a href =\"{info}\">" + i + "</a>")

        except Exception:
            QMessageBox.about(self, 'Error', 'Wrong gene input or couldn\'t find data')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())

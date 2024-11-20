from flask import Flask
from sys import argv

app = Flask(__name__)



@app.route("/")
def home():
    return str("hii")




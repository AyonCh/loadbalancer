from flask import Flask
from sys import argv

app = Flask(__name__)

HOST = argv[1]
PORT = int(argv[2])


@app.route("/")
def home():
    return str(PORT)


app.run(HOST, PORT)

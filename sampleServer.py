from flask import Flask
from sys import argv

app = Flask(__name__)

port = int(argv[1])


@app.route("/")
def home():
    return str(port)


app.run("127.0.0.1", port)

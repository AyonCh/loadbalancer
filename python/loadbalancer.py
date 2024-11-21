from flask import (
    Flask,
    json,
    jsonify,
    request,
    request_finished,
)
from sys import argv
import subprocess
import requests


PORT = int(argv[1])
HOST = "127.0.0.1"
config = {
    "totalServers": 10,
    "startupCommand": [
        "node",
        "server/index.js",
        "{port}",
    ],
}
buckets = []
processes = {}
index = 1

app = Flask(__name__)


def createServer(host, port):
    command = (
        " ".join(config["startupCommand"])
        .replace("{host}", host)
        .replace("{port}", port)
        .split(" ")
    )

    processes[port] = subprocess.Popen(command)
    print("Creating server on port", port)


def killServer(port):
    processes[port].terminate()
    del processes[port]

    print("Deleting server on port", port)


def log_response(sender, response, **extra):
    if "port" in extra:
        index = extra["port"] - PORT - 1
        buckets.sort(key=lambda x: x["port"])
        buckets[index]["count"] -= 1


request_finished.connect(log_response, app)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def proxy(path):
    buckets.sort(key=lambda x: x["count"])

    url = f"""http://{HOST}:{buckets[0]["port"]}/{path}"""
    buckets[0]["count"] += 1

    res = requests.get(url).json()

    request_finished.send(app, response=res, port=res["port"])

    return jsonify({"res": res})


for i in range(config["totalServers"]):
    buckets.append({"port": PORT + i + 1, "count": 0})
    createServer(HOST, str(PORT + i + 1))

app.run("127.0.0.1", PORT)

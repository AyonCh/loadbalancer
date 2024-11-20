from flask import (
    Flask,
    json,
    jsonify,
    request,
    request_finished,
)
from sys import argv
from time import sleep
import subprocess
import requests


PORT = int(argv[1])
HOST = "127.0.0.1"
config = {
    "maxLoad": 10,
    "maxBuckets": 10,
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
    sleep(1)
    print("Creating server on port", port)


def killServer(port):
    processes[port].terminate()
    del processes[port]

    print("Deleting server on port", port)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def proxy(path):
    global index
    buckets.sort(key=lambda x: x["count"])

    if len(buckets) < 1:
        createServer(HOST, str(PORT + index))
        buckets.append({"count": 0, "port": PORT + index})

        index += 1

    if len(buckets) < config["maxBuckets"] and buckets[0]["count"] == config["maxLoad"]:
        createServer(HOST, str(PORT + index))
        buckets.insert(0, {"count": 0, "port": PORT + index})

        index += 1

    url = f"""http://{HOST}:{buckets[0]["port"]}/"""
    buckets[0]["count"] += 1

    res = requests.get(url)

    buckets[0]["count"] -= 1

    # if count = 0 close server
    if buckets[0]["count"] <= 0:
        killServer(str(buckets[0]["port"]))
        buckets.pop(0)

    if len(buckets) > 0:
        buckets.sort(key=lambda x: x["port"], reverse=True)
        index = buckets[0]["port"] - PORT + 1
    else:
        index = 1

    return jsonify({"res": res.content.decode()})


app.run("127.0.0.1", PORT, debug=True)

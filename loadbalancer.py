from flask import (
    Flask,
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
config = {"maxLoad": 2, "maxBuckets": 10}
buckets = []
processes = {}
index = 1

app = Flask(__name__)


def createServer(host, port):
    processes[port] = subprocess.Popen(
        ["python3", "sampleServer.py", host, port],
        stdin=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
    )
    print("Creating server on port", port)


def killServer(port):
    processes[port].terminate()
    del processes[port]

    print("Deleting server on port", port)


def log_response(sender, response, **extra):
    global index
    # find the smallest bucket
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


request_finished.connect(log_response, app)


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

    sleep(100)
    print(url)
    res = requests.get(url)

    print(res)
    return jsonify({"path": path, "string": url})


app.run("127.0.0.1", PORT, debug=True)

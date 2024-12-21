from flask import (
    Flask,
    json,
    request_finished,
)
from sys import argv
import subprocess
import requests


PORT = int(argv[1])
HOST = "127.0.0.1"
config = {
    "maxLoad": 2,
    "availablePorts": [PORT + i for i in range(1, 11)],
    "startupCommand": ["python3", "sampleServer.py", "{port}"],
}

buckets = []
processes = {}
ports = config["availablePorts"]

app = Flask(__name__)


def createServer(host):
    global buckets

    ports.sort()
    port = ports.pop(0)

    command = (
        " ".join(config["startupCommand"])
        .replace("{host}", host)
        .replace("{port}", str(port))
        .split(" ")
    )

    processes[port] = subprocess.Popen(command)
    buckets.append({"port": port, "count": 0})
    print("Creating server on port", port)


def killServer(port):
    processes[port].kill()
    del processes[port]
    ports.append(port)

    print("Deleting server on port", port)


def log_response(sender, response, **extra):
    if "port" in extra:
        port = extra["port"]
        index = port - PORT - 1
        buckets.sort(key=lambda x: x["port"])
        buckets[index]["count"] -= 1

        if len(buckets) > 1 and buckets[index]["count"] == 0:
            killServer(port)
            buckets.pop(index)


request_finished.connect(log_response, app)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def proxy(path):
    buckets.sort(key=lambda x: x["count"])

    if len(ports) > 0 and buckets[0]["count"] >= config["maxLoad"]:
        createServer(HOST)

    port = buckets[0]["port"]
    url = f"""http://{HOST}:{port}/{path}"""
    buckets[0]["count"] += 1

    res = requests.get(url).text

    request_finished.send(app, response=res, port=port)

    return json.dumps(res)


createServer(HOST)

app.run("127.0.0.1", PORT)

import subprocess

config = {
    "maxLoad": 2,
    "maxBuckets": 10,
    "startupCommand": [
        "node",
        "server/index.js",
        "{port}",
    ],
}

host = "127.0.0.1"
port = "8000"

command = (
    " ".join(config["startupCommand"])
    .replace("{host}", host)
    .replace("{port}", port)
    .split(" ")
)

print(command)

p = subprocess.Popen(command)

p.terminate()

const http = require("http");
const port = process.argv[2];
const config = require("../config.json");

let ports = config["availablePorts"];
let buckets = [];

const createBucket = () => {
  let bucketPort = ports.sort((a, b) => a - b).shift();
  buckets.push({ port: bucketPort, count: 0 });
};

const killBucket = (bucketPort) => {
  let newBuckets = [];
  buckets.forEach((bucket) => {
    if (bucket["port"] != bucketPort) {
      newBuckets.push(bucket);
    }
  });

  buckets = newBuckets;
  ports.push(bucketPort);
};

const server = http.createServer((req, res) => {
  buckets.sort((a, b) => a["count"] - b["count"]);

  if (ports.length > 0 && buckets[0]["count"] >= config["maxLoad"] - 1) {
    createBucket();
  }

  let url = `http://localhost:${buckets[0]["port"]}/`;

  buckets[0]["count"]++;
  res.writeHead(200, { "Content-Type": "application/json" });
  res.end(
    JSON.stringify({
      data: buckets[0]["port"],
      url,
    }),
  );

  res.on("end", () => {
    buckets[0]["count"]--;

    if (buckets.length > 1 && buckets[0]["count"] == 0) {
      killBucket(buckets[0]["port"]);
    }
  });
});

createBucket();
server.listen(port);

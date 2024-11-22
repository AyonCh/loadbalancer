const express = require("express");

const app = express();

const port = process.argv[2];

app.get("/", (req, res) => {
  res.send({ content: `Hello from port: ${port}` });
});

app.get("*", (req, res) => {
  res.send(`This page shouldn't exists, but hi from port: ${port}`);
});

app.listen(port, () => console.log(`server started on port: ${port}`));

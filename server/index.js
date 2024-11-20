const express = require("express");

const app = express();

const port = process.argv[2];

app.get("/", (req, res) => {
  res.send(`Hi from port: ${port}`);
});

app.listen(port, () => console.log(`server started on port: ${port}`));

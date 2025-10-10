const express = require("express");
const cors = require("cors");
const db = require("./db");

const app = express();

app.use(cors()); //Enables all cors requests

app.get("/", async (req, res) => {
  try {
    //Querys the databases and brings back the results as JSON
    const result1 = await db.query(
      "SELECT json_agg(sensor_example) FROM sensor_example"
    );

    res.json(result1.rows);
  } catch (err) {
    console.error(err);
    res.status(500).send("Internal Server Error");
  }
});

//Posts some data into the database
app.get("/postData", async (req, res) => {
  try {
    //Creates data
    for (let i = 0; i < 10; i++) {
      function data() {
        return new Promise((resolve, reject) => {
          setTimeout(() => {
            let sensorID = "fridge";
            let sensorValue = Math.random();
            let sensorDate = new Date()
              .toISOString()
              .slice(0, 19)
              .replace("T", " "); //Get current timestamp 'https://stackoverflow.com/questions/5129624/convert-js-date-time-to-mysql-datetime'
            resolve([sensorID, sensorValue, sensorDate]);
          }, 1000);
        });
      }

      //Inserts data to database
      async function insertData() {
        const result = await data();
        await db.query(
          `INSERT INTO sensor_example (sensorId ,sensorValue,sensorDate) VALUES ('${result[0]}', ${result[1]},'${result[2]}');`
          //Instead of {result[2]} (which is a timestamp created by JS) I can use NOW()::TIMESTAMP (SQL prodcues the timestamp)
        );
      }

      await insertData();
    }

    // const result = await db.query(
    //   "SELECT sensorvalue,sensordate FROM sensor_example"
    // );
    res.send("done");
  } catch (err) {
    console.error(err);
    res.status(500).send("Internal Server Error");
  }
});

app.listen(3000, () => {
  console.log("Listening on port 3000");
});

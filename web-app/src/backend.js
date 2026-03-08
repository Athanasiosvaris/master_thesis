const express = require("express");
const cors = require("cors");
const db = require("./db");

const app = express();

app.use(cors()); //Enables all cors requests

app.get("/sensor1Data", async (req, res) => {
  try {
    //Querys the databases and brings back the results as JSON
    const realValues = await db.query(
      "SELECT json_agg(t)FROM ( SELECT * FROM sensor1realvalues ORDER BY sensordate DESC LIMIT 10) AS t"
    );

    const forecastedValues = await db.query(
      "SELECT json_agg(t)FROM ( SELECT * FROM sensor1forecastedvalues ORDER BY sensordate DESC LIMIT 10) AS t"
    );
    let realValuesData = realValues.rows[0].json_agg; //Array of objects
    let forecastedValuesData = forecastedValues.rows[0].json_agg;
    let finaldata = forecastedValuesData.concat(realValuesData); // The first 10 values of the array are the real data and the next 10 values are the fprecasted data

    res.json(finaldata);
  } catch (err) {
    console.error(err);
    res.status(500).send("Internal Server Error");
  }
});

//Posts some data into the database
app.get("/postData", async (req, res) => {
  try {
    //Creates data
    for (let i = 0; i < 5; i++) {
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
          `INSERT INTO sensor1realvalues (sensorId ,sensorValue,sensorDate) VALUES ('${result[0]}', ${result[1]},'${result[2]}');`
        );
      }

      await insertData();
    }

    res.send("done");
  } catch (err) {
    console.error(err);
    res.status(500).send("Internal Server Error");
  }
});

app.listen(3000, () => {
  console.log("Listening on port 3000");
});

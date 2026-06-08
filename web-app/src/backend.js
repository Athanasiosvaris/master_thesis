const express = require("express");
const cors = require("cors");
const db = require("./db");

const app = express();

app.use(cors()); //Enables all cors requests

app.get("/sensor1Data", async (req, res) => {
  try {
    //Querys the databases and brings back the results as JSON
    const realValues = await db.query(
      "SELECT json_agg(t) FROM ( SELECT sensor_energy_value AS sensorvalue, sensor_timestamp AS sensordate FROM device1_actualvalues ORDER BY sensor_timestamp DESC LIMIT 60) AS t"
    );

    const forecastedValues = await db.query(
      "SELECT json_agg(t) FROM ( SELECT sensor_energy_value_prediction AS sensorvalue, sensor_timestamp AS sensordate FROM device1_forecastedvalues ORDER BY sensor_timestamp DESC LIMIT 60) AS t"
    );
    let realValuesData = realValues.rows[0].json_agg || []; //Array of objects
    let forecastedValuesData = forecastedValues.rows[0].json_agg || [];

    // Only return data when both actual and forecasted values are available (120 total)
    if (realValuesData.length < 60 || forecastedValuesData.length < 60) {
      res.json([]);
      return;
    }

    //let finaldata = realValuesData.concat(forecastedValuesData);
    let finaldata = forecastedValuesData.concat(realValuesData); // The first 60 values are the real data and the next 60 values are the forecasted data

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

app.listen(3001, () => {
  console.log("Listening on port 3001");
});

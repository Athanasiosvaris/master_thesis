import Chart from "chart.js/auto";

async function getData() {
  //Retrives the data from the database - Calls backend API
  try {
    const response = await fetch("http://localhost:3000");
    const result = await response.json();
    let data = [];
    for (let i in result[0].json_agg) {
      let picked = {};
      picked["sensorvalue"] = result[0].json_agg[i].sensorvalue;
      picked["sensordate"] = result[0].json_agg[i].sensordate;
      data.push(picked);
    }
    return data;
  } catch (e) {
    console.log(e.message);
  }
}

async function plotLineDiagram(dataSet) {
  //Plots a line diagram
  new Chart(document.getElementById("lineChartDB"), {
    type: "line",
    options: {},
    data: {
      labels: dataSet.map((row) => row.sensordate),
      datasets: [
        {
          label: "Sensor 1 Real values per second",
          data: dataSet.map((row) => row.sensorvalue),
        },
      ],
    },
  });
}

async function plotLineDiagram2(dataSet) {
  //Plots a line diagram
  new Chart(document.getElementById("lineChartDBForecast"), {
    type: "line",
    options: {},
    data: {
      labels: dataSet.map((row) => row.sensordate),
      datasets: [
        {
          label: "Sensor 1 Forecasted values per second",
          data: dataSet.map((row) => row.sensorvalue),
        },
      ],
    },
  });
}

// updateChartData = () => {};

async function DrawPlots() {
  const dataSet1 = await getData(); // Retreived Dataset
  plotLineDiagram(dataSet1);
  plotLineDiagram2(dataSet1);
}

DrawPlots();

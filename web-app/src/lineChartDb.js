import Chart from "chart.js/auto";

const btn1 = document.getElementById("btn1");
let Chart1;
let Chart2;
let help = false;

btn1.addEventListener("click", () => {
  if (help) {
    autoUpdate();
    Chart1.update();
  } else window.alert("Please try again");
});

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

function plotLineDiagram(dataSet) {
  //Plots a line diagram
  const Chart1 = new Chart(document.getElementById("lineChartDB"), {
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
  return Chart1;
}

function plotLineDiagram2(dataSet) {
  //Plots a line diagram
  const Chart2 = new Chart(document.getElementById("lineChartDBForecast"), {
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
  return Chart2;
}

async function DrawPlots() {
  const dataSet1 = await getData(); // Retreived Dataset
  Chart1 = plotLineDiagram(dataSet1);
  Chart2 = plotLineDiagram2(dataSet1);
}

DrawPlots().then(() => {
  help = true;
});

async function autoUpdate() {
  // It updates the chart
  const newDataset = await getData();
  let data = [];
  for (let obj of newDataset) {
    // data.push(obj.sensorvalue);
    data.push(0.5);
  }
  console.log(data);
  Chart1.config._config.data.datasets[0].data = data;
  Chart1.update();
}

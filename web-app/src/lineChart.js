import Chart from "chart.js/auto";

//Declares and immediately invokes an async function
// (async function name(params) {})();

const dataSet1 = [
  {
    sensorvalue: 0.8030039,
    sensordate: "2025-10-06T10:32:48.654Z",
  },
  {
    sensorvalue: 0.26208028,
    sensordate: "2025-10-06T10:37:52.417Z",
  },
  {
    sensorvalue: 0.43252516,
    sensordate: "2025-10-06T10:38:15.563Z",
  },
  {
    sensorvalue: 0.19100115,
    sensordate: "2025-10-06T10:38:47.689Z",
  },
  {
    sensorvalue: 0.7502743,
    sensordate: "2025-10-06T10:44:23.203Z",
  },
];

const dataSet2 = [
  {
    sensorvalue: 0.1,
    sensordate: "2025-10-06T10:32:48.654Z",
  },
  {
    sensorvalue: 0.1,
    sensordate: "2025-10-06T10:37:52.417Z",
  },
  {
    sensorvalue: 0.1,
    sensordate: "2025-10-06T10:38:15.563Z",
  },
  {
    sensorvalue: 0.1,
    sensordate: "2025-10-06T10:38:47.689Z",
  },
  {
    sensorvalue: 0.1,
    sensordate: "2025-10-06T10:44:23.203Z",
  },
];

//Declares and immediately invokes an async function
async function plotLineDiagram(dataSet) {
  new Chart(document.getElementById("lineChart"), {
    type: "line",
    options: {},
    data: {
      labels: dataSet.map((row) => row.sensordate),
      datasets: [
        {
          label: "Sensor value per second",
          data: dataSet.map((row) => row.sensorvalue),
        },
      ],
    },
  });
}

plotLineDiagram(dataSet1);

// setTimeout(function () {
//   console.log("Reloaded");
//   plotLineDiagram(dataSet2);
//   //location.reload(1);
// }, 5000);

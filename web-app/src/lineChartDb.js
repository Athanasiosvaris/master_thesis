// const { set } = require("mongoose");
const func = require("./functions");

const btn1 = document.getElementById("btn1");
let Chart1;
let Chart2;
let help = false;

btn1.addEventListener("click", () => {
  window.location.href = "./index.html";
});

async function DrawPlots() {
  const dataSet1 = await func.getData(); // Retreived Dataset
  Chart1 = func.plotLineDiagram(dataSet1, "lineChartDB", "Sensor 1");
}

DrawPlots().then(() => {
  help = true;
});

async function autoUpdate() {
  // It updates the chart
  const newDataset = await func.getData(); //New data from the database
  // console.log(newDataset);
  let data = [];
  let labels1 = [];
  for (let obj of newDataset) {
    data.push(obj.sensorvalue);
    labels1.push(obj.sensordate);
  }
  console.log("Updated");
  Chart1.config._config.data.datasets[0].data = data;

  Chart1.config._config.data.labels = labels1;
  Chart1.update();
}

// setInterval(autoUpdate, 5000);

// async function postData2() {
//   try {
//     const response = await fetch("http://localhost:3000/postData");
//     console.log(response);
//   } catch (e) {
//     console.log(e.message);
//   }
// }
// console.log("postData2");
// postData2();

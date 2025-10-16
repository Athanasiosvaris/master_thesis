import Chart from "chart.js/auto";

export async function getData() {
  //Retrives the data from the database - Calls backend API
  try {
    const response = await fetch("http://localhost:3000/sensor1Data");
    const result = await response.json();
    let data = [];
    for (let i = result.length - 1; i >= 0; i--) {
      let picked = {};
      picked["sensorvalue"] = result[i].sensorvalue;
      picked["sensordate"] = result[i].sensordate.replace("T", " ");
      data.push(picked);
    }
    console.log(data);
    return data;
  } catch (e) {
    console.log(e.message);
  }
}

export function plotLineDiagram(dataSet, elementID, labelName) {
  //Plots a line diagram
  const Chart1 = new Chart(document.getElementById(elementID), {
    type: "line",
    options: {
      elements: {
        point: {
          backgroundColor: (ctx) => {
            // console.log(ctx);
            if (ctx.dataIndex >= 10) return "rgba(192, 93, 75, 1)";
            else return "rgba(56, 92, 192, 1)";
          },
        },
      },
    },
    data: {
      labels: dataSet.map((row) => row.sensordate),
      datasets: [
        {
          label: `${labelName}`,
          data: dataSet.map((row) => row.sensorvalue),
          segment: {
            borderColor: (ctx) => {
              // console.log(ctx);
              if (ctx.p1DataIndex >= 10) return "rgba(192, 93, 75, 1)";
              else return "rgba(56, 92, 192, 1)";
            },
          },
        },
      ],
    },
  });
  return Chart1;
}

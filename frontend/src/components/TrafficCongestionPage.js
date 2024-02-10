import React, { useEffect, useState } from "react";
import Chart from "chart.js/auto";

const TrafficCongestionPage = () => {
  const [vehicleData, setVehicleData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("http://localhost:3001/api/vehicleData");

        if (!response.ok) {
          console.error("Server returned an error:", response.statusText);
          return;
        }

        const contentType = response.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
          console.error("Invalid content type. Expected application/json.");
          return;
        }

        const data = await response.json();
        setVehicleData(data);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    createChart();
  }, [vehicleData]);

  const createChart = () => {
    const canvas = document.getElementById("myLineChart");
    const ctx = canvas ? canvas.getContext("2d") : null;

    if (!ctx) {
      console.error("Canvas not found");
      return;
    }

    if (canvas.chart) {
      canvas.chart.data.labels = getUniqueTimestamps(vehicleData);
      canvas.chart.data.datasets[0].data = getVehicleCounts(vehicleData);
      canvas.chart.update();
    } else {
      const newChart = new Chart(ctx, {
        type: "line",
        data: {
          labels: getUniqueTimestamps(vehicleData),
          datasets: [
            {
              label: "Number of Vehicles",
              data: getVehicleCounts(vehicleData),
              borderColor: "rgba(150, 200, 250, 1)",
              borderWidth: 2,
              fill: true,
            },
          ],
        },
        options: {
          responsive: true,
          scales: {
            xAxes: [
              {
                type: "linear",
                position: "bottom",
                display: true,
              },
            ],
            yAxes: [
              {
                display: true,
                ticks: {
                  beginAtZero: true,
                },
              },
            ],
          },
        },
      });

      canvas.chart = newChart;
    }
  };

  const getUniqueTimestamps = (data) => {
    const uniqueTimestamps = [
      ...new Set(data.map((vehicle) => vehicle.timestamp)),
    ];
    return uniqueTimestamps;
  };

  const getVehicleCounts = (data) => {
    const timestampCounts = {};
    data.forEach((vehicle) => {
      const timestamp = vehicle.timestamp;
      timestampCounts[timestamp] = (timestampCounts[timestamp] || 0) + 1;
    });

    const vehicleCounts = getUniqueTimestamps(data).map(
      (timestamp) => timestampCounts[timestamp]
    );
    return vehicleCounts;
  };

  return (
    <div className="trafficCongestion-page-content">
      <h2>Traffic Congestion Page</h2>
      <div style={{ maxWidth: "1080px", margin: "0 auto" }}>
        <canvas
          id="myLineChart"
          style={{ width: "100%", height: "auto" }}
        ></canvas>
      </div>
    </div>
  );
};

export default TrafficCongestionPage;

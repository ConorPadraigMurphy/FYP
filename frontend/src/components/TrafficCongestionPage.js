import React, { useEffect, useState } from "react";
import Chart from "chart.js/auto";

const TrafficCongestionPage = () => {
  const [vehicleData, setVehicleData] = useState([]);

  useEffect(() => {
    console.log("Inside useEffect");

    const fetchData = async () => {
      try {
        console.log("Fetching data...");
        const response = await fetch("/api/vehicleData"); 
        console.log("Server Response:", response);

        if (!response.ok) {
          console.error("Server returned an error:", response.statusText);
          return;
        }

        const data = await response.json();
        console.log("Fetched data from server:", data);

        setVehicleData(data);
        console.log("Updated state after data processing:", data);
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
    const ctx = canvas.getContext("2d");

    // Destroy existing chart if it exists
    if (canvas.chart) {
      canvas.chart.destroy();
    }

    // Extract entered times and vehicle counts from the vehicleData
    const enteredTimes = vehicleData.map((vehicle) => vehicle.entered_time);
    const vehicleCounts = Array(vehicleData.length).fill(1);
    console.log("Entered Times:", enteredTimes);
    console.log("Vehicle Counts:", vehicleCounts);
    const newChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: enteredTimes,
        datasets: [
          {
            label: "Number of Vehicles",
            data: vehicleCounts,
            borderColor: "rgba(150, 200, 250, 1)",
            borderWidth: 2,
            fill: true,
          },
        ],
      },
      options: {
        scales: {
          x: {
            type: "linear",
            position: "bottom",
          },
          y: {
            beginAtZero: true,
          },
        },
      },
    });
    // Attach the chart instance to the canvas element
    canvas.chart = newChart;
  };

  return (
    <div className="trafficCongestion-page-content">
      <h2>Traffic Congestion Page</h2>
      <div style={{ maxWidth: "1080px", margin: "0 auto" }}>
        <canvas id="myLineChart" width="400" height="200"></canvas>
      </div>
    </div>
  );
};

export default TrafficCongestionPage;

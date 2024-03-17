import React, { useEffect, useState } from "react";
import Chart from "chart.js/auto";
import { GoogleMap, LoadScript, Marker } from "@react-google-maps/api";

const TrafficCongestionPage = () => {
  const [vehicleData, setVehicleData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [address, setAddress] = useState("");
  const maxGraphWidth = "1080px"; // Maximum width of the graph

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
        setFilteredData(filterDataByAddress(data, address));
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, [address]);

  useEffect(() => {
    createChart();
  }, [selectedLocation]);

  const filterDataByAddress = (data, address) => {
    if (!address) {
      return data;
    }

    return data.filter((vehicle) => vehicle.address.includes(address));
  };

  const groupDataByLocation = (data) => {
    const groupedData = {};
    data.forEach((vehicle) => {
      const locationKey = vehicle.address;
      if (!groupedData[locationKey]) {
        groupedData[locationKey] = {
          location: {
            lat: parseFloat(vehicle.latitude),
            lng: parseFloat(vehicle.longitude),
          },
          address: vehicle.address,
          timestamps: [],
        };
      }
      groupedData[locationKey].timestamps.push(vehicle.timestamp);
    });
    return Object.values(groupedData);
  };

  const createChart = () => {
    const canvas = document.getElementById("myLineChart");
    const ctx = canvas ? canvas.getContext("2d") : null;

    if (!ctx) {
      console.error("Canvas not found");
      return;
    }

    if (canvas.chart) {
      canvas.chart.data.labels = getUniqueTimestamps(
        selectedLocation.timestamps
      );
      canvas.chart.data.datasets[0].data = getVehicleCounts(
        selectedLocation.timestamps
      );
      canvas.chart.update();
    } else {
      if (selectedLocation) {
        const newChart = new Chart(ctx, {
          type: "line",
          data: {
            labels: getUniqueTimestamps(selectedLocation.timestamps),
            datasets: [
              {
                label: "Number of Vehicles",
                data: getVehicleCounts(selectedLocation.timestamps),
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
    }
  };

  const getUniqueTimestamps = (data) => {
    const uniqueTimestamps = [...new Set(data.map((timestamp) => timestamp))];
    uniqueTimestamps.sort((a, b) => a - b);
    return uniqueTimestamps;
  };

  const getVehicleCounts = (data) => {
    const timestampCounts = {};
    data.forEach((timestamp) => {
      timestampCounts[timestamp] = (timestampCounts[timestamp] || 0) + 1;
    });

    const vehicleCounts = getUniqueTimestamps(data).map(
      (timestamp) => timestampCounts[timestamp]
    );
    return vehicleCounts;
  };

  const handleMarkerClick = (location) => {
    setSelectedLocation(location);
  };

  const renderGoogleMap = () => {
    const groupedLocations = groupDataByLocation(filteredData);
    return (
      <LoadScript googleMapsApiKey="AIzaSyBJ39gTzB4yRuN_JTevio4hEcJYSgM8B3o">
        <GoogleMap
          mapContainerStyle={{ height: "400px", width: "100%" }}
          center={{ lat: 53.274, lng: -9.0568 }}
          zoom={10}
        >
          {groupedLocations.map((location) => (
            <Marker
              key={`${location.address}`}
              position={location.location}
              title={location.address}
              onClick={() => handleMarkerClick(location)}
            />
          ))}
        </GoogleMap>
      </LoadScript>
    );
  };

  return (
    <div className="trafficCongestion-page-content">
      <h2>Traffic Congestion Page</h2>
      <p>
        Select a pin below to access user-sourced data and visualize the hourly
        count of vehicles in the area.
      </p>
      <div style={{ maxWidth: maxGraphWidth, margin: "0 auto" }}>
        <div style={{ display: "flex", justifyContent: "center" }}>
          <div style={{ width: maxGraphWidth }}>{renderGoogleMap()}</div>
        </div>
        <div style={{ width: maxGraphWidth }}>
          <canvas
            id="myLineChart"
            style={{ width: "100%", height: "auto" }}
          ></canvas>
        </div>
      </div>
    </div>
  );
};

export default TrafficCongestionPage;

import React, { useEffect, useState } from "react";
import Chart from "chart.js/auto";
import { GoogleMap, LoadScript, Marker } from "@react-google-maps/api";

const TrafficCongestionPage = () => {
  const [vehicleData, setVehicleData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [address, setAddress] = useState("");
  const [charts, setCharts] = useState({}); // Keep track of created charts
  const maxGraphWidth = "1080px"; // Maximum width of the graph

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(
          process.env.REACT_APP_ENDPOINT_URL + "/api/vehicleData"
        );

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
        const carData = data.filter((vehicle) => vehicle.class_id === "Car"); // Filter vehicles that have class_id "Bus"
        setVehicleData(carData);
        setFilteredData(filterDataByAddress(data, address));
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, [address]);

  useEffect(() => {
    if (selectedLocation) {
      createCharts();
    }
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
      groupedData[locationKey].timestamps.push(vehicle);
    });
    return Object.values(groupedData);
  };

  const createCharts = () => {
    // Destroy existing charts
    Object.values(charts).forEach((chart) => chart.destroy());
    const groupedData = groupDataByDay(selectedLocation.timestamps);
    const newCharts = {};
    Object.keys(groupedData).forEach((day) => {
      const canvas = document.getElementById(`myLineChart-${day}`);
      const ctx = canvas ? canvas.getContext("2d") : null;

      if (!ctx) {
        console.error("Canvas not found");
        return;
      }

      const newChart = new Chart(ctx, {
        type: "line",
        data: {
          labels: getUniqueTimestamps(groupedData[day]),
          datasets: [
            {
              label: "Number of Vehicles",
              data: getVehicleCounts(groupedData[day]),
              borderColor: "rgba(150, 200, 250, 1)",
              borderWidth: 2,
              fill: true,
            },
          ],
        },
        options: {
          responsive: true,
          scales: {
            x: {
              type: "linear",
              position: "bottom",
              display: true,
              beginAtZero: false,
              ticks: {
                stepSize: 1,
              },
              title: {
                display: true,
                text: "Time (24hr)",
              },
            },
            y: {
              display: true,
              beginAtZero: true,
              ticks: {
                stepSize: 5,
              },
              title: {
                display: true,
                text: "# of Vehicles",
              },
            },
          },
        },
      });

      newCharts[day] = newChart;
    });

    setCharts(newCharts);
  };

  const groupDataByDay = (data) => {
    const groupedData = {};
    data.forEach((vehicle) => {
      const weekday = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
      ];
      const day = weekday[new Date(vehicle.entered_time).getDay()];
      if (!groupedData[day]) {
        groupedData[day] = [];
      }
      groupedData[day].push(vehicle);
    });
    return groupedData;
  };

  const getUniqueTimestamps = (data) => {
    const uniqueTimestamps = [
      ...new Set(
        data.map((vehicle) => {
          const enteredTime = new Date(vehicle.entered_time);
          return enteredTime.getHours();
        })
      ),
    ];
    uniqueTimestamps.sort((a, b) => a - b);
    return uniqueTimestamps;
  };

  const getVehicleCounts = (data) => {
    const timestampCounts = {};
    data.forEach((vehicle) => {
      const enteredTime = new Date(vehicle.entered_time);
      const hour = enteredTime.getHours();
      //const timestamp = vehicle.entered_time;
      timestampCounts[hour] = (timestampCounts[hour] || 0) + 1;
    });

    const vehicleCounts = getUniqueTimestamps(data).map(
      (hour) => timestampCounts[hour] || 0
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
          {groupedLocations.map((location, index) => (
            <Marker
              key={`${location.address}-${index}`}
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

      <div>
        <div style={{ display: "flex", justifyContent: "center" }}>
          <div style={{ width: maxGraphWidth }}>{renderGoogleMap()}</div>
        </div>

        <div style={{ display: "flex", justifyContent: "center" }}>
          <div style={{ width: maxGraphWidth }}>
            {selectedLocation &&
              Object.keys(groupDataByDay(selectedLocation.timestamps)).map(
                (day, index) => (
                  <div key={index}>
                    <h3>{day}</h3>
                    <canvas id={`myLineChart-${day}`}></canvas>
                  </div>
                )
              )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrafficCongestionPage;

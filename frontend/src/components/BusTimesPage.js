import React, { useEffect, useState } from "react";
import Chart from "chart.js/auto";
import { GoogleMap, LoadScript, Marker } from "@react-google-maps/api";

const BusTimesPage = () => {
  const [vehicleData, setVehicleData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [address, setAddress] = useState("");
  const [charts, setCharts] = useState({}); // Keep track of created charts
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
        const busData = data.filter((vehicle) => vehicle.class_id === "Bus"); // Filter vehicles that have class_id "Bus"
        setVehicleData(busData);
        setFilteredData(filterDataByAddress(busData, address));
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
              borderColor: "rgba(255, 150, 150, 1)",
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
                //callback: (value) => Math.floor(value), // Format tick label
              },
              title: {
                display: true,
                text: "Time in Hours",
              },
            },
            y: {
              display: true,
              beginAtZero: true,
              ticks: {
                stepSize: 5,
                //callback: (value) => Math.floor(value), // Format tick label
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
      const day = vehicle.dayOfWeek;
      if (!groupedData[day]) {
        groupedData[day] = [];
      }
      groupedData[day].push(vehicle);
    });
    return groupedData;
  };

  const getUniqueTimestamps = (data) => {
    const uniqueTimestamps = [
      ...new Set(data.map((vehicle) => vehicle.timestamp)),
    ];
    uniqueTimestamps.sort((a, b) => a - b);
    return uniqueTimestamps;
  };

  const getVehicleCounts = (data) => {
    const timestampCounts = {};
    data.forEach((vehicle) => {
      timestampCounts[vehicle.timestamp] =
        (timestampCounts[vehicle.timestamp] || 0) + 1;
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
    <div className="bus-times-page">
      <h2>Bus Schedule Page</h2>
      <p>
        Click on a pin below to explore user-provided data and visualize the
        hourly frequency of bus appearances.
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

export default BusTimesPage;

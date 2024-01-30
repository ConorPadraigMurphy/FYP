import React, { useEffect } from 'react';
import Chart from 'chart.js/auto';

class TrafficCongestionPage extends React.Component {
    componentDidMount() {
        // Create a chart when the component mounts
        this.createChart();
    }

    createChart() {
        // Get the canvas element
        const canvas = document.getElementById('myLineChart');
        const ctx = canvas.getContext('2d');

        // Check if a chart instance already exists
        if (canvas.chart) {
            // Destroy the existing chart instance
            canvas.chart.destroy();
        }

        // Mock data for the line chart
        const mockData = {
            labels: ['6AM', '7AM', '8AM', '9AM', '10AM', '11AM', '12PM', '1PM', '2PM', '4PM', '5PM', '6PM'],
            datasets: [{
                label: 'Vehicles Per Hour',
                data: [10, 15, 8, 20, 12, 15, 8, 20, 12, 20, 12, 15],
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2,
                fill: true,
            }],
        };

        // Create a line chart with mock data
        const newChart = new Chart(ctx, {
            type: 'line',
            data: mockData,
            options: {
                scales: {
                    x: {
                        type: 'category',
                        labels: mockData.labels,
                    },
                    y: {
                        beginAtZero: true,
                    },
                },
            },
        });

        // Attach the chart instance to the canvas element
        canvas.chart = newChart;
    }

    render() {
        return (
            <div className="trafficCongestion-page-content">
                <h2>Traffic Congestion Page</h2>
                {/* Create a container with a maximum width */}
                <div style={{ maxWidth: '1080px', margin: '0 auto' }}>
                    {/* Create a canvas element for the line chart */}
                    <canvas id="myLineChart" width="400" height="200"></canvas>
                </div>
            </div>
        );
    }
}

export default TrafficCongestionPage;

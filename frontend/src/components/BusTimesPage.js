import React from 'react';
import Chart from 'chart.js/auto';

class BusTimesPage extends React.Component {
    componentDidMount() {
        // Create a bar chart when the component mounts
        this.createBarChart();
    }

    createBarChart() {
        // Get the canvas element
        const canvas = document.getElementById('BusBarChart');
        const ctx = canvas.getContext('2d');

        // Check if a chart instance already exists
        if (canvas.chart) {
            // Destroy the existing chart instance
            canvas.chart.destroy();
        }

        // Mock data for the bar chart
        const mockData = {
            labels: ['Stop 1', 'Stop 2', 'Stop 3', 'Stop 4', 'Stop 5'],
            datasets: [{
                label: 'Bus Arrival Times',
                data: [5, 10, 15, 8, 12],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(255, 205, 86, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                ],
                borderColor: [
                    'rgba(75, 192, 192, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 205, 86, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(153, 102, 255, 1)',
                ],
                borderWidth: 1,
            }],
        };

        // Create a bar chart with mock data
        const newChart = new Chart(ctx, {
            type: 'bar',
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
            <div className="busTimes-page-content">
                <h2>Bus Times Page</h2>
                {/* Create a canvas element for the bar chart */}
               
                <div style={{ maxWidth: '1080px', margin: '0 auto' }}>
                    {/* Create a canvas element for the line chart */}
                    <canvas id="BusBarChart" width="400" height="200"></canvas>
                </div>
            </div>
        );
    }
}

export default BusTimesPage;

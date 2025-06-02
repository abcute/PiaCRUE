import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function SimpleLogChart({ analysisData, chartTitle = "Log Event Analysis" }) {
  if (!analysisData || Object.keys(analysisData).length === 0) {
    return (
      <div className="p-4 text-center text-gray-500">
        Upload and analyze a log file to see a basic chart here.
        <br />
        (Or data from a conceptual backend endpoint is not available yet).
      </div>
    );
  }

  // Assuming analysisData is an object like: { eventTypeA: count, eventTypeB: count }
  const data = {
    labels: Object.keys(analysisData),
    datasets: [
      {
        label: 'Event Counts',
        data: Object.values(analysisData),
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false, // Allow chart to fit container height
    plugins: {
      legend: {
        position: 'top',
        labels: {
            color: '#ccc' // Legend text color
        }
      },
      title: {
        display: true,
        text: chartTitle,
        color: '#eee', // Title color
        font: {
            size: 16
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0,0,0,0.7)',
        titleColor: '#fff',
        bodyColor: '#fff',
      }
    },
    scales: {
      x: {
        ticks: {
          color: '#ccc', // X-axis labels color
          font: {
            size: 10
          }
        },
        grid: {
          color: 'rgba(255,255,255,0.1)' // X-axis grid lines color
        }
      },
      y: {
        beginAtZero: true,
        ticks: {
          color: '#ccc', // Y-axis labels color
        },
        grid: {
          color: 'rgba(255,255,255,0.1)' // Y-axis grid lines color
        }
      },
    },
  };

  return (
    <div className="simple-log-chart p-4 border border-slate-700 rounded-lg" style={{ height: '300px' }}> {/* Set a fixed height for the chart container */}
      <Bar data={data} options={options} />
    </div>
  );
}

export default SimpleLogChart;

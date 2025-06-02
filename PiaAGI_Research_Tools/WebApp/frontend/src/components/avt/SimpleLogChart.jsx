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
  // analysisData is expected to be in the shape: { event_counts: { EventTypeA: 10, ... } }
  // or null/undefined if no data.
  
  const chartableData = analysisData?.event_counts;

  if (!chartableData || Object.keys(chartableData).length === 0) {
    return (
      <div className="p-4 text-center text-gray-500">
        Upload and analyze a log file to see a basic chart of event counts.
      </div>
    );
  }

  const data = {
    labels: Object.keys(chartableData),
    datasets: [
      {
        label: 'Event Counts',
        data: Object.values(chartableData),
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

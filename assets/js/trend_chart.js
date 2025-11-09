// Global chart instance
let currentChart = null;

// Get references to DOM elements
const ctx = document.getElementById('myChart').getContext('2d');
const chartContainer = document.getElementById('chartContainer');
const chartTypeDropdown = document.getElementById('chartTypeDropdown');

// Add event listener for dropdown changes
chartTypeDropdown.addEventListener('change', function() {
    const selectedType = this.value;

    // Destroy existing chart if it exists
    if (currentChart) {
        currentChart.destroy();
        currentChart = null;
    }

    // Handle different chart types
    if (selectedType === 'none') {
        // Hide chart container
        chartContainer.style.display = 'none';
    } else if (selectedType === 'amount') {
        // Show container and load Amount Incoming chart
        chartContainer.style.display = 'block';
        loadAmountIncomingChart();
    } else if (selectedType === 'bookings') {
        // Show container and load Bookings By Month chart
        chartContainer.style.display = 'block';
        loadBookingsByMonthChart();
    }
});

// Function to load Amount Incoming (Line Chart)
function loadAmountIncomingChart() {
    $.ajax({
        url: "/trend_chart",
        type: "POST",
        data: {},
        error: function() {
            alert("Error loading Amount Incoming chart");
        },
        success: function(data, status, xhr) {
            const chartDim = data.chartDim;

            // Transform data for Chart.js
            const vLabels = [];
            const vData = [];

            for (const [key, values] of Object.entries(chartDim)) {
                vLabels.push(key);
                let xy = [];
                for (let i = 0; i < values.length; i++) {
                    let d = new Date(values[i][0]);
                    let year = d.getFullYear();
                    let month = ('' + (d.getMonth() + 1)).padStart(2, '0');
                    let day = ('' + d.getDate()).padStart(2, '0');
                    let aDateTime = year + '-' + month + '-' + day;
                    xy.push({'x': aDateTime, 'y': values[i][1]});
                }
                vData.push(xy);
            }

            // Create line chart
            currentChart = new Chart(ctx, {
                data: {
                    datasets: []
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                parser: 'yyyy-MM-dd',
                            },
                            title: {
                                display: true,
                                text: 'Date'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Revenue ($)'
                            }
                        }
                    }
                }
            });

            // Add datasets for each hotel
            for (let i = 0; i < vLabels.length; i++) {
                currentChart.data.datasets.push({
                    label: vLabels[i],
                    type: "line",
                    borderColor: '#' + (0x1100000 + Math.random() * 0xffffff).toString(16).substr(1, 6),
                    backgroundColor: "rgba(249, 238, 236, 0.74)",
                    data: vData[i],
                    spanGaps: true
                });
            }
            currentChart.update();
        }
    });
}

// Function to load Bookings By Month (Bar Chart)
function loadBookingsByMonthChart() {
    $.ajax({
        url: "/bookings_by_month",
        type: "POST",
        data: {},
        error: function() {
            alert("Error loading Bookings By Month chart");
        },
        success: function(data, status, xhr) {
            const chartData = data.chartData;

            // Extract all unique hotels (sorted alphabetically - already done in backend)
            const hotels = Object.keys(chartData);

            // Extract all unique months across all hotels
            const allMonths = new Set();
            for (const hotel in chartData) {
                for (const month in chartData[hotel]) {
                    allMonths.add(month);
                }
            }

            // Sort months chronologically
            const monthsList = Array.from(allMonths).sort((a, b) => {
                return new Date(a) - new Date(b);
            });

            // Generate random colors for each month
            const colors = monthsList.map(() => {
                return '#' + (0x1100000 + Math.random() * 0xffffff).toString(16).substr(1, 6);
            });

            // Create datasets - one for each month
            const datasets = monthsList.map((month, index) => {
                const dataPoints = hotels.map(hotel => {
                    return chartData[hotel][month] || 0;
                });

                return {
                    label: month,
                    data: dataPoints,
                    backgroundColor: colors[index],
                    borderColor: colors[index],
                    borderWidth: 1
                };
            });

            // Create bar chart
            currentChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: hotels,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Hotels'
                            }
                        },
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Number of Bookings'
                            },
                            ticks: {
                                stepSize: 1
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        }
                    }
                }
            });
        }
    });
}

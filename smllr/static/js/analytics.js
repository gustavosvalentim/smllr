let chart;

function initChart(data) {
  const ctx = document
    .getElementById("chart-click-by-platform")
    .getContext("2d");

  const chartData = {
    labels: ["Windows", "Linux", "Android"],
    datasets: [
      {
        label: "Clicks by Platform",
        data: [data.windows_clicks, data.linux_clicks, data.android_clicks],
        backgroundColor: [
          "rgba(54, 162, 235, 0.6)",
          "rgba(255, 99, 132, 0.6)",
          "rgba(255, 206, 86, 0.6)",
        ],
      },
    ],
  };

  const chartConfig = {
    type: "pie",
    data: chartData,
  };

  if (!chart) {
    chart = new Chart(ctx, chartConfig);
  } else {
    chart.data = chartData;
    chart.update();
  }
}

async function fetchChartData() {
  const code = document.getElementById("shorturl_code").textContent;
  const response = await fetch(`/api/analytics/${code}`);
  if (!response.ok) {
    throw new Error("Network response was not ok");
  }
  const data = await response.json();
  return data;
}

function analyticsData() {
  return {
    totalClicks: 0,
    windowsClicks: 0,
    linuxClicks: 0,
    androidClicks: 0,
    latestClicks: [],
    init() {
      fetchChartData()
        .then((data) => {
          this.totalClicks = data.total_clicks;
          this.windowsClicks = data.windows_clicks;
          this.linuxClicks = data.linux_clicks;
          this.androidClicks = data.android_clicks;
          this.latestClicks = data.latest_clicks;
          initChart(data);
        })
        .catch((error) => {
          console.error("Error fetching analytics data:", error);
        });
    },
    refresh() {
      this.init();
    },
  };
}

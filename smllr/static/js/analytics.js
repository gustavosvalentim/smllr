let platformChart;
let timeSeriesChart;
let deviceChart;
let browserChart;

function initPlatformChart(platformData) {
  const ctx = document
    .getElementById("chart-click-by-platform")
    .getContext("2d");

  const labels = [];
  const data = [];
  const colors = [
    "rgba(54, 162, 235, 0.6)",
    "rgba(255, 99, 132, 0.6)",
    "rgba(255, 206, 86, 0.6)",
    "rgba(75, 192, 192, 0.6)",
    "rgba(153, 102, 255, 0.6)",
    "rgba(255, 159, 64, 0.6)",
  ];

  // Add platforms with non-zero clicks
  if (platformData.windows > 0) {
    labels.push("Windows");
    data.push(platformData.windows);
  }
  if (platformData.macos > 0) {
    labels.push("macOS");
    data.push(platformData.macos);
  }
  if (platformData.linux > 0) {
    labels.push("Linux");
    data.push(platformData.linux);
  }
  if (platformData.android > 0) {
    labels.push("Android");
    data.push(platformData.android);
  }
  if (platformData.ios > 0) {
    labels.push("iOS");
    data.push(platformData.ios);
  }
  if (platformData.other > 0) {
    labels.push("Other");
    data.push(platformData.other);
  }

  const chartData = {
    labels: labels,
    datasets: [
      {
        label: "Clicks by Platform",
        data: data,
        backgroundColor: colors.slice(0, labels.length),
      },
    ],
  };

  const chartConfig = {
    type: "pie",
    data: chartData,
  };

  if (!platformChart) {
    platformChart = new Chart(ctx, chartConfig);
  } else {
    platformChart.data = chartData;
    platformChart.update();
  }
}

function initTimeSeriesChart(timeSeriesData) {
  const ctx = document
    .getElementById("chart-clicks-by-day")
    .getContext("2d");

  const labels = timeSeriesData.map((item) => item.date);
  const data = timeSeriesData.map((item) => item.clicks);

  const chartData = {
    labels: labels,
    datasets: [
      {
        label: "Clicks per Day",
        data: data,
        borderColor: "rgba(54, 162, 235, 1)",
        backgroundColor: "rgba(54, 162, 235, 0.2)",
        tension: 0.4,
      },
    ],
  };

  const chartConfig = {
    type: "line",
    data: chartData,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1,
          },
        },
      },
    },
  };

  if (!timeSeriesChart) {
    timeSeriesChart = new Chart(ctx, chartConfig);
  } else {
    timeSeriesChart.data = chartData;
    timeSeriesChart.update();
  }
}

function initDeviceChart(deviceData) {
  const ctx = document.getElementById("chart-clicks-by-device").getContext("2d");

  const labels = [];
  const data = [];
  const colors = [
    "rgba(255, 99, 132, 0.6)",
    "rgba(54, 162, 235, 0.6)",
    "rgba(255, 206, 86, 0.6)",
    "rgba(153, 102, 255, 0.6)",
  ];

  if (deviceData.mobile > 0) {
    labels.push("Mobile");
    data.push(deviceData.mobile);
  }
  if (deviceData.desktop > 0) {
    labels.push("Desktop");
    data.push(deviceData.desktop);
  }
  if (deviceData.tablet > 0) {
    labels.push("Tablet");
    data.push(deviceData.tablet);
  }
  if (deviceData.other > 0) {
    labels.push("Other");
    data.push(deviceData.other);
  }

  const chartData = {
    labels: labels,
    datasets: [
      {
        label: "Clicks by Device",
        data: data,
        backgroundColor: colors.slice(0, labels.length),
      },
    ],
  };

  const chartConfig = {
    type: "doughnut",
    data: chartData,
  };

  if (!deviceChart) {
    deviceChart = new Chart(ctx, chartConfig);
  } else {
    deviceChart.data = chartData;
    deviceChart.update();
  }
}

function initBrowserChart(browserData) {
  const ctx = document.getElementById("chart-clicks-by-browser").getContext("2d");

  const labels = Object.keys(browserData);
  const data = Object.values(browserData);

  const chartData = {
    labels: labels,
    datasets: [
      {
        label: "Clicks",
        data: data,
        backgroundColor: "rgba(54, 162, 235, 0.6)",
        borderColor: "rgba(54, 162, 235, 1)",
        borderWidth: 1,
      },
    ],
  };

  const chartConfig = {
    type: "bar",
    data: chartData,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: "y",
      scales: {
        x: {
          beginAtZero: true,
          ticks: {
            stepSize: 1,
          },
        },
      },
    },
  };

  if (!browserChart) {
    browserChart = new Chart(ctx, chartConfig);
  } else {
    browserChart.data = chartData;
    browserChart.update();
  }
}

async function fetchChartData() {
  const code = document.getElementById("shorturl_code").textContent;
  const response = await fetch(`/api/analytics/${code}`);
  if (!response.ok) {
    throw new Error("Network response was not ok");
  }
  return await response.json();
}

function analyticsData() {
  return {
    totalClicks: 0,
    uniqueVisitors: 0,
    avgClicksPerDay: 0,
    peakHour: null,
    windowsClicks: 0,
    macosClicks: 0,
    linuxClicks: 0,
    androidClicks: 0,
    iosClicks: 0,
    otherPlatformClicks: 0,
    mobileClicks: 0,
    desktopClicks: 0,
    tabletClicks: 0,
    otherDeviceClicks: 0,
    directClicks: 0,
    socialMediaClicks: {},
    searchEngineClicks: {},
    otherReferrers: [],
    browsers: {},
    latestClicks: [],
    init() {
      fetchChartData()
        .then((data) => {
          // Basic metrics
          this.totalClicks = data.total_clicks || 0;
          this.uniqueVisitors = data.unique_visitors || 0;
          this.avgClicksPerDay = data.avg_clicks_per_day || 0;
          this.peakHour = data.peak_hour;

          // Platform data
          const platform = data.clicks_by_platform || {};
          this.windowsClicks = platform.windows || 0;
          this.macosClicks = platform.macos || 0;
          this.linuxClicks = platform.linux || 0;
          this.androidClicks = platform.android || 0;
          this.iosClicks = platform.ios || 0;
          this.otherPlatformClicks = platform.other || 0;

          // Device data
          const device = data.clicks_by_device || {};
          this.mobileClicks = device.mobile || 0;
          this.desktopClicks = device.desktop || 0;
          this.tabletClicks = device.tablet || 0;
          this.otherDeviceClicks = device.other || 0;

          // Source data
          const source = data.clicks_by_source || {};
          this.directClicks = source.direct || 0;
          this.socialMediaClicks = source.social_media || {};
          this.searchEngineClicks = source.search_engines || {};
          this.otherReferrers = source.other_referrers || [];

          // Browser data
          this.browsers = data.clicks_by_browser || {};

          // Latest clicks
          this.latestClicks = data.latest_clicks || [];

          // Initialize charts
          if (data.clicks_by_platform) {
            initPlatformChart(data.clicks_by_platform);
          }
          if (data.clicks_by_day) {
            initTimeSeriesChart(data.clicks_by_day);
          }
          if (data.clicks_by_device) {
            initDeviceChart(data.clicks_by_device);
          }
          if (data.clicks_by_browser && Object.keys(data.clicks_by_browser).length > 0) {
            initBrowserChart(data.clicks_by_browser);
          }
        })
        .catch((error) => {
          console.error("Error fetching analytics data:", error);
        });
    },
    refresh() {
      this.init();
    },
    formatPeakHour() {
      if (this.peakHour === null) return "N/A";
      const hour = this.peakHour;
      const period = hour >= 12 ? "PM" : "AM";
      const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
      return `${displayHour}:00 ${period}`;
    },
  };
}

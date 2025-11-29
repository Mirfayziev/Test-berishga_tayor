function fetchDashboardData(callback) {
  if (!window.dashboardDataUrl) return;
  fetch(window.dashboardDataUrl)
    .then(r => r.json())
    .then(data => callback && callback(data))
    .catch(err => console.error("Dashboard data error:", err));
}

// Dashboard charts
document.addEventListener("DOMContentLoaded", function () {
  if (typeof window.dashboardDataUrl === "undefined") {
    return;
  }

  fetchDashboardData(function (data) {
    // Tasks status chart on dashboard
    const ctxTasks = document.getElementById("tasksStatusChart");
    if (ctxTasks) {
      const counts = data.task_counts || {};
      const labels = ["new", "in_progress", "review", "done"];
      const values = labels.map(k => counts[k] || 0);

      new Chart(ctxTasks, {
        type: "doughnut",
        data: {
          labels: ["Yangi", "Jarayonda", "Ko'rib chiqishda", "Bajarilgan"],
          datasets: [{
            data: values,
            borderWidth: 0,
          }]
        },
        options: {
          plugins: {
            legend: {
              labels: { color: "#e5e7eb", font: { size: 11 } }
            }
          }
        }
      });
    }

    // Solar chart & forecast
    const solarData = data.solar || [];
    const forecast = data.solar_forecast || [];

    const solarLabels = solarData.map(s => s.day);
    const solarValues = solarData.map(s => s.energy_kwh);
    const forecastLabels = forecast.map(s => s.day);
    const forecastValues = forecast.map(s => s.energy_kwh);

    const ctxSolarDashboard = document.getElementById("solarChart");
    const ctxSolarPage = document.getElementById("solarChartPage");
    const solarCtx = ctxSolarPage || ctxSolarDashboard;

    if (solarCtx) {
      new Chart(solarCtx, {
        type: "line",
        data: {
          labels: solarLabels.concat(forecastLabels),
          datasets: [
            {
              label: "Real",
              data: solarValues.concat(Array(forecastValues.length).fill(null)),
              tension: 0.35,
            },
            {
              label: "Forecast (AI)",
              data: Array(solarValues.length).fill(null).concat(forecastValues),
              borderDash: [5, 5],
              tension: 0.35,
            }
          ]
        },
        options: {
          scales: {
            x: { ticks: { color: "#9ca3af", autoSkip: true, maxTicksLimit: 8 } },
            y: { ticks: { color: "#9ca3af" } }
          },
          plugins: {
            legend: {
              labels: { color: "#e5e7eb", font: { size: 11 } }
            }
          }
        }
      });
    }

    // Activity heatmap
    const activity = data.activity || [];
    const ctxHeatDashboard = document.getElementById("activityHeatmap");
    const ctxHeatPage = document.getElementById("activityHeatmapPage");
    const heatCtx = ctxHeatPage || ctxHeatDashboard;

    if (heatCtx && activity.length) {
      // Very simple heatmap: day on x, tasks count on y as bar color intensity
      const labels = activity.map(a => a.day);
      const values = activity.map(a => a.completed_tasks);

      new Chart(heatCtx, {
        type: "bar",
        data: {
          labels,
          datasets: [{
            label: "Bajarilgan topshiriqlar",
            data: values,
          }]
        },
        options: {
          scales: {
            x: { ticks: { color: "#9ca3af", autoSkip: true, maxTicksLimit: 10 } },
            y: { ticks: { color: "#9ca3af" } }
          },
          plugins: {
            legend: {
              labels: { color: "#e5e7eb", font: { size: 11 } }
            }
          }
        }
      });
    }
  });
});

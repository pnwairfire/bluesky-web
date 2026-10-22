<script lang="ts">
  export let daily

  import { browser } from '$app/environment';
  import { Chart, registerables } from 'chart.js';
  import { onMount } from 'svelte';
  import dayjs from 'dayjs'

  Chart.register(...registerables);

  let barChartElement;
  let chart;

  function fillInMonths (daily) {
    const dailyDict = daily.reduce((r, d) => {
      r[dayjs(d.date)] = d
      return r
    }, {})

    const first = dayjs(daily[0].date)
    const last = dayjs(daily.at(-1).date)

    const dailyComplete = []
    let d = first
    while (d >= last) {
      dailyComplete.push(dailyDict[d] ||
        {date: d.format('YYYY-MM-DD'), count: 0})
      d = d.subtract(1, 'day')
    }
    return dailyComplete.reverse()
  }

  $: dailyComplete = fillInMonths(daily)

  $: chartData = {
    labels: dailyComplete.map(({ date }) => date),
    datasets: [
      {
        label: '# Runs',
        data: dailyComplete.map(({ count }) => count),
        borderRadius: 2,
        borderWidth: 2,
      },
    ],
  };

  onMount(() => {
    if (browser) {
      chart = new Chart(barChartElement, {
        type: 'bar',
        data: chartData,
        options: {
          plugins: {
            legend: {
              display: false,
            },
            tooltip: {
              callbacks: {
                // Per-queue counts listed below the total run count
                afterLabel: (context) => (dailyComplete[context.dataIndex].by_queue || [])
                  .map(({ queue, count }) => `  ${queue || '(none)'}: ${count}`),
              },
            },
          },
          scales: {
            y: {
              beginAtZero: false,
              title: {
                display: true,
                text: '# Runs',
              },
            },
          },
        },
      });
    }
    return () => chart && chart.destroy();
  });

  $: if (chart) {
    chart.data = chartData;
    chart.update();
  }
</script>

<main class="main-container">
  <section>
    <canvas bind:this={barChartElement} />
  </section>
</main>

<style>
  .main-container {
    width: min(100% - var(--spacing-12), var(--max-width-wrapper));
    margin: var(--spacing-18) auto;
  }
</style>
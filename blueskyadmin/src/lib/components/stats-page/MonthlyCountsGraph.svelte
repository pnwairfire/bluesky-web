<script lang="ts">
  export let monthly

  import { browser } from '$app/environment';
  import { Chart, registerables } from 'chart.js';
  import { onMount } from 'svelte';
  import dayjs from 'dayjs'

  Chart.register(...registerables);

  let barChartElement;

  function fillInMonths (monthly) {
    const monthlyDict = monthly.reduce((r, m) => {
      const d = dayjs(`${m.year}-${m.month}-01`)
      r[d] = m
      return r
    }, {})
    const first = dayjs(`${monthly[0].year}-${monthly[0].month}-01`)
    const last = dayjs(`${monthly.at(-1).year}-${monthly.at(-1).month}-01`)

    const monthlyComplete = []
    let d = first

    while (d >= last) {
      monthlyComplete.push(monthlyDict[d] ||
        {year: d.format('YYYY'), month: d.format('MM'), count: 0})
      d = d.subtract(1, 'month')
    }
    return monthlyComplete
  }

  const monthlyComplete = fillInMonths(monthly)

  const chartData = {
    labels: monthlyComplete.map(({ year, month }) => `${month}/${year}`),
    datasets: [
      {
        label: '# Runs',
        data: monthlyComplete.map(({ count }) => count),
        borderRadius: 2,
        borderWidth: 2,
      },
    ],
  };

  onMount(() => {
    if (browser) {
      new Chart(barChartElement, {
        type: 'bar',
        data: chartData,
        options: {
          plugins: {
            legend: {
              display: false,
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
  });
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
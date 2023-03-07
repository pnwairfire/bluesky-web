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
        backgroundColor: [
          'hsl(347 38% 49%)',
          'hsl(346 65% 63%)',
          'hsl(346 49% 56%)',
          'hsl(346 89% 70%)',
          'hsl(346 90% 76%)',
          'hsl(346 90% 73%)',
          'hsl(346 89% 79%)',
          'hsl(346 89% 85%)',
          'hsl(347 89% 82%)',
          'hsl(346 90% 88%)',
          'hsl(347 87% 94%)',
          'hsl(347 91% 91%)',
          'hsl(346 87% 97%)',
        ],
        borderColor: ['hsl(43 100% 52%)'],
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
            x: {
              grid: {
                color: 'hsl(43 100% 52% / 10%)',
              },
              ticks: { color: 'hsl(43 100% 52% )' },
            },
            y: {
              beginAtZero: false,
              ticks: { color: 'hsl(43 100% 52% )', font: { size: 18 } },
              grid: {
                color: 'hsl(43 100% 52% / 40%)',
              },
              title: {
                display: true,
                text: 'Satisfaction (%)',
                color: 'hsl(43 100% 52% )',
              },
            },
          },
        },
      });
    }
  });
</script>

<main class="main-container">
  <h5>Number of runs per month in the past year</h5>
  <section>
    <canvas bind:this={barChartElement} />
  </section>
</main>
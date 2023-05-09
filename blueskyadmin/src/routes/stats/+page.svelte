<script>
    /** @type {import('./$types').PageData} */
    export let data;

    import { base } from '$app/paths';
    import { PUBLIC_STATS_RUNID_OPTIONS } from '$env/static/public';
    import { Alert, Col, Container, Row, Table } from 'sveltestrap';

    import MonthlyCountsGraph from '$lib/components/stats-page/MonthlyCountsGraph.svelte'

    import DailyCountsGraph from '$lib/components/stats-page/DailyCountsGraph.svelte'

    const runIdOptions = PUBLIC_STATS_RUNID_OPTIONS && JSON.parse(PUBLIC_STATS_RUNID_OPTIONS)

    $: displayedRunId = runIdOptions[data.runId] || data.runId || 'All Runs'
</script>


<Container fluid="true">
    {#if runIdOptions}
      <nav class="navbar navbar-expand-lg bg-body-tertiary" style="background-color: white !important;">
        <div class="dropdown my-2">
            <button class="btn btn-primary dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
            { displayedRunId }
            </button>
            <ul class="dropdown-menu">
                <li><a class="dropdown-item" href={`${base}/stats/`}>All Runs</a></li>
                {#each Object.keys(runIdOptions) as r, i}
                    <li><a class="dropdown-item" href={`${base}/stats/?runId=${r}`}>{runIdOptions[r]}</a></li>
                {/each}
            </ul>
        </div>
      </nav>
    {/if}
    {#if data.error}
      {data.error}
    {:else}
      <div class="header">
        <span class="text">Monthly</span>
        <span class="caption">(Past Year)</span>
      </div>
      {#if !data.stats.monthly || data.stats.monthly.length ===0 }
        <div>No Data</div>
      {:else}
        <Row>
          <Col>
            <div class="m-3">
                <Table bordered hover striped size="sm" responsive>
                  <thead>
                    <tr>
                      <th>Year</th>
                      <th>Month</th>
                      <th>Count</th>
                      <th>Top Queue</th>
                    </tr>
                  </thead>
                  <tbody>
                    {#each data.stats.monthly as monthlyStats}
                        <tr>
                          <td>{monthlyStats.year}</td>
                          <td>{monthlyStats.month}</td>
                          <td>{monthlyStats.count}</td>
                          <td>{monthlyStats.by_queue[0].queue} ({monthlyStats.by_queue[0].count})</td>
                        </tr>
                    {/each}
                  </tbody>
                </Table>
            </div>
          </Col>
          <Col>
            <MonthlyCountsGraph monthly={data.stats.monthly} />
          </Col>
        </Row>
      {/if}
      <div class="header">
        <span class="text">Daily</span>
        <span class="caption">(Past 30 days)</span>
      </div>
      {#if !data.stats.daily || data.stats.daily.length ===0 }
        <div>No Data</div>
      {:else}
        <Row>
          <Col>
            <div class="m-3">
                <Table bordered hover striped size="sm" responsive>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Count</th>
                      <th>Top Queue</th>
                    </tr>
                  </thead>
                  <tbody>
                    {#each data.stats.daily as dailyStats}
                        <tr>
                          <td>{dailyStats.date}</td>
                          <td>{dailyStats.count}</td>
                          <td>{dailyStats.by_queue[0].queue} ({dailyStats.by_queue[0].count})</td>
                        </tr>
                    {/each}
                  </tbody>
                </Table>
            </div>
          </Col>
          <Col>
            <DailyCountsGraph daily={data.stats.daily} />
          </Col>
        </Row>
      {/if}
    {/if}
</Container>

<style>
  .header .text {
     font-size: x-large;
     font-weight: bold;
  }
  .header .caption {
    font-style: italic;
  }
</style>
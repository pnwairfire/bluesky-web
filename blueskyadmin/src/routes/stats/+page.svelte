<script>
    import { Alert, Col, Container, Row, Table } from 'sveltestrap';

    import MonthlyCountsGraph from '$lib/components/stats-page/MonthlyCountsGraph.svelte'

    /** @type {import('./$types').PageData} */
    export let data;
</script>


<Container fluid="true">
    {#if data.error}
        {data.error}
    {:else}
        <h4>Monthly</h4>
        <Row>
          <Col>
            <div class="m-3">
                <Table bordered hover striped size="sm" responsive>
                  <thead>
                    <tr>
                      <th>Year</th>
                      <th>Month</th>
                      <th>Count</th>
                    </tr>
                  </thead>
                  <tbody>
                    {#each data.stats.monthly as monthlyStats}
                        <tr>
                          <td>{monthlyStats.year}</td>
                          <td>{monthlyStats.month}</td>
                          <td>{monthlyStats.count}</td>
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
        <h4>Daily</h4>
        <div class="m-3">
            <Table bordered hover striped size="sm" responsive>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Count</th>
                </tr>
              </thead>
              <tbody>
                {#each data.stats.daily as dailyStats}
                    <tr>
                      <td>{dailyStats.date}</td>
                      <td>{dailyStats.count}</td>
                    </tr>
                {/each}
              </tbody>
            </Table>
        </div>
    {/if}
</Container>

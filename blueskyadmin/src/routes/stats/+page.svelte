<script>
    import { Alert, Col, Container, Row, Table } from 'sveltestrap';

    import MonthlyCountsGraph from '$lib/components/stats-page/MonthlyCountsGraph.svelte'

    import DailyCountsGraph from '$lib/components/stats-page/DailyCountsGraph.svelte'

    /** @type {import('./$types').PageData} */
    export let data;
</script>


<Container fluid="true">
    {#if data.error}
        {data.error}
    {:else}
        <div>
          <span style="font-size: x-large; font-weight: bold;">Monthly</span>
          <span style="font-style: italic;">(Past Year)</span>
        </div>
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
        <div>
          <span style="font-size: x-large; font-weight: bold;">Daily</span>
          <span style="font-style: italic;">(Past 30 days)</span>
        </div>
        <Row>
          <Col>
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
          </Col>
          <Col>
            <DailyCountsGraph daily={data.stats.daily} />
          </Col>
        </Row>
    {/if}
</Container>

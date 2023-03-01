<script>
    import { Alert, Container, Table } from 'sveltestrap';

    /** @type {import('./$types').PageData} */
    export let data;
</script>


<Container fluid="true">
    {#if data.error}
        {data.error}
    {:else}
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
    {/if}
</Container>

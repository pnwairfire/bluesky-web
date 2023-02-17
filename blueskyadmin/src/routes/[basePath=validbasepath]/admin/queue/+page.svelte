<script>
    import { Alert, Container, Table } from 'sveltestrap';

    /** @type {import('./$types').PageData} */
    export let data;

    const labels = {
        in_queue: "In Queue",
        executing: "Currently Executing",
        scheduled: "Scheduled For Later",
    }
</script>


<Container fluid="true">
    {#if data.error}
        {data.error}
    {:else}
        {#each Object.keys(data.queueInfo) as category, i}
            <Alert class="mt-3" color="dark">{labels[category] || category}</Alert>
            {#each Object.keys(data.queueInfo[category]) as pool, j}
                <div class="m-3">
                    <b>{pool}</b>
                {#if data.queueInfo[category][pool].length === 0}
                    (None)
                {:else}
                    <div class="m-3">
                        <Table bordered hover striped size="sm" responsive>
                          <thead>
                            <tr>
                              <th>Run Id</th>
                              <th>Modules</th>
                              <th>API version</th>
                              <th>Priority</th>
                              {#if category === 'scheduled'}
                                <th>Scheduled For</th>
                              {/if}
                            </tr>
                          </thead>
                          <tbody>
                            {#each data.queueInfo[category][pool] as run}
                                <tr>
                                  <td>{run.run_id}</td>
                                  <td>{run.modules.join(', ')}</td>
                                  <td>{run.api_version}</td>
                                  <td>{run.priority || 'n/a'}</td>
                                  {#if category === 'scheduled'}
                                    <td>{run.schedule_for}</td>
                                  {/if}
                                </tr>
                            {/each}
                          </tbody>
                        </Table>
                    </div>
                {/if}
                </div>
            {/each}
        {/each}
    {/if}
</Container>

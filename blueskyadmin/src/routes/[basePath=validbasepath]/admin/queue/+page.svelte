<script>
    import { Container, Table } from 'sveltestrap';

    /** @type {import('./$types').PageData} */
    export let data;

</script>

<Container fluid="true">
    {#if data.error}
        {data.error}
    {:else}
        {#each Object.keys(data.queueInfo) as category, i}
            <b>{category}</b>
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
                              <th>Scheduled For</th>
                            </tr>
                          </thead>
                          <tbody>
                            {#each data.queueInfo[category][pool] as run}
                                <tr>
                                  <th>{run.run_id}</th>
                                  <th>{run.modules.join(', ')}</th>
                                  <th>{run.api_version}</th>
                                  <th>{run.priority}</th>
                                  <th>{run.schedule_for}</th>
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

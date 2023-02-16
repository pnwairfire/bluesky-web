<script>
    import { Button, Container, Table } from 'sveltestrap';
    import { runStatuses } from '$lib/run-status'

    /** @type {import('./$types').PageData} */
    export let data;

    let status = runStatuses[data.runStatus]
    const total = data.runsData.total
    const first = (data.runsData) && (data.limit*data.page +1)
    const last = (data.runsData) && Math.min(data.limit*data.page + data.limit, total)
</script>

{@debug data}

    <Container fluid={true}>
		<!-- sveltestrap  dropdown wasn't working, so using bootstrap classes directly -->
		<div class="dropdown my-2">
			<button class="btn btn-light dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
		    {status}
			</button>
			<ul class="dropdown-menu">
				{#each Object.keys(runStatuses) as s, i}
					<li><a class="dropdown-item" href={s}>{runStatuses[s]}</a></li>
				{/each}
			</ul>
		</div>

        {#if data.error}
            {data.error}
        {:else if !data.runsData || ! data.runsData.runs}
            <div>No data</div>
        {:else if data.runsData.runs.length === 0}
            <div>No runs on record</div>
        {:else}
            <div>
                <div class="my-3">
                    {#if data.page > 0}
                        <a href={`?page=${data.page-1}`}>
                            <Button outline dark>&lt;</Button>
                        </a>
                    {/if}
                    <span>{first} - {last} of {total}</span>
                    {#if last < total}
                        <a href={`?page=${data.page+1}`}>
                            <Button outline dark>&gt;</Button>
                        </a>
                    {/if}
                </div>
                <Table bordered hover striped size="sm" responsive>
                  <thead>
                    <tr>
                      <th>Run Id</th>
                      <th>status</th>
                      <th>Percent Complete</th>
                      <th>Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    {#each data.runsData.runs as run}
                        <tr>
                          <td>{run.run_id}</td>
                          <td>{run.status.status}</td>
                          <td>{run.status.perc}</td>
                          <td>{run.status.ts}</td>
                        </tr>
                    {/each}
                  </tbody>
                </Table>
            </div>
        {/if}
    </Container>

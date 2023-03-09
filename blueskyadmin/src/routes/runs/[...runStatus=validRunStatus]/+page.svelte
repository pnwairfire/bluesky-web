<script>
    /** @type {import('./$types').PageData} */
    export let data;

    console.dir("Data: ", data)

    import { base } from '$app/paths';
    import { goto } from '$app/navigation';
    import { Container, Table, Form, FormGroup, Input } from 'sveltestrap';
    import { runStatuses } from '$lib/run-status'

    $: status = data.runStatus ? runStatuses[data.runStatus] : 'All Runs'
    $: total = data.runsData.total
    $: first = (data.runsData) && (data.limit*data.page +1)
    $: last = (data.runsData) && Math.min(data.limit*data.page + data.limit, total)

    $: runIdQueryStr = data.runId ? `runId=${data.runId}` : ''
</script>

    <Container fluid={true}>
        <nav class="navbar navbar-expand-lg bg-body-tertiary" style="background-color: white !important;">
            <div class="container-fluid">
                <!-- sveltestrap  dropdown wasn't working, so using bootstrap classes directly -->
                <div class="dropdown my-2">
                    <button class="btn btn-primary dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                    {status}
                    </button>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href={`${base}/runs/?${runIdQueryStr}`}>All Runs</a></li>
                        {#each Object.keys(runStatuses) as s, i}
                            <li><a class="dropdown-item" href={`${base}/runs/${s}/?${runIdQueryStr}`}>{runStatuses[s]}</a></li>
                        {/each}
                    </ul>
                </div>

                <div class="row g-3">
                    <div class="col-auto">
                        <form class="row g-3 align-items-right">
                            <div class="col-auto">
                                <label for="runId" class="col-form-label">Run Id</label>
                            </div>
                            <div class="col-auto">
                                <input id="runId" name="runId" class="form-control" value={data.runId} placeholder="Enter complete or partial run id">
                            </div>
                            <div class="col-auto">
                                <button type="submit" class="btn btn-primary">Find</button>
                            </div>
                        </form>
                    </div>
                    <div class="col-auto">
                        <form class="row g-3 align-items-center">
                            <a class={"btn btn-warning " + (data.runId ? '' : 'disabled')} href={`${base}/runs/${data.runStatus || ''}/`}>Clear</a>
                        </form>
                    </div>
                </div>
            </div>
        </nav>

        {#if data.error}
            {data.error}
        {:else if !data.runsData || ! data.runsData.runs}
            <div>No data</div>
        {:else if data.runsData.runs.length === 0}
            <div>No runs on record</div>
        {:else}
            <div>
                <div class="my-3">
                    <a class={`btn btn-outline-dark ${(data.page === 0) ? (' disabled') : ('')}`}
                            href={`?page=${data.page-1}&${runIdQueryStr}`}>
                        &lt;
                    </a>
                    <span>{first} - {last} of {total}</span>
                    <a class={`btn btn-outline-dark ${(last >= total) ? (' disabled') : ('')}`}
                            href={`?page=${data.page+1}&${runIdQueryStr}`}>
                        &gt;
                    </a>
                </div>
                <Table bordered hover striped size="sm" responsive>
                    <thead>
                        <tr>
                            <th>Run Id</th>
                            <th>Queue</th>
                            <th>status</th>
                            <th>Percent Complete</th>
                            <th>Time</th>
                            <th>Output</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each data.runsData.runs as run}
                            <tr>
                                <td>{run.run_id}</td>
                                <td>{run.queue ? run.queue.name : 'n/a'}</td>
                                <td>{run.status.status}</td>
                                <td>{run.status.perc}</td>
                                <td>{run.status.ts}</td>
                                <td>
                                    {#if run.output_url}
                                        <a href={run.output_url} target="_blank">output</a>
                                    {:else}
                                        n/a
                                    {/if}
                                </td>
                            </tr>
                      {/each}
                    </tbody>
                </Table>
            </div>
        {/if}
    </Container>

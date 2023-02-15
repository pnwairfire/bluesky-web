<script>
    import { Container, Nav, NavItem, NavLink, Table } from 'sveltestrap';
    import { runStatuses } from '$lib/run-status'

    /** @type {import('./$types').PageData} */
    export let data;

    let status = runStatuses[data.runStatus]
</script>

{@debug data}

<Container fluid="true">
    <Nav>
        {#each Object.keys(runStatuses) as s, i}
          <NavItem>
            <NavLink href={s}>{runStatuses[s]}</NavLink>
          </NavItem>
        {/each}
    </Nav>
    <h1>{status}</h1>
    <Container>
        {#if data.error}
            {data.error}
        {:else if !data.runsData || ! data.runsData.runs}
            <div>No data</div>
        {:else if data.runsData.runs.length === 0}
            <div>No runs on record</div>
        {:else}
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
        {/if}
    </Container>
</Container>

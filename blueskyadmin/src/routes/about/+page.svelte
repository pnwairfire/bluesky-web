<script>
    import { Container, ListGroup, ListGroupItem } from 'sveltestrap';

    import { runStatuses } from '$lib/run-status'
</script>

<svelte:head>
	<title>About</title>
	<meta name="description" content="About BlueSky Web" />
</svelte:head>

<Container fluid={true}>
	<h5>About This Site</h5>

	<h6>Workers Queues</h6>
	<p>
		This page provides transparency into the worker queues, listing
		runs that are a) scheduled to be run later, b) in the queue
		to be executed as soon as a worker is free, and c) actively being
		exectuted.
	</p>

	<h6>Runs Database</h6>
	<p>
		These pages reflect what is recorded in the runs database.
		This includes runs at any point in their lifecycle -
		a) scheduled to be run later, b) in the queue
		to be executed as soon as a worker is free, c) actively being
		exectuted, or d) already completed.  Runs are broken down by
		status:
	</p>
	<Container fluid>
		<ListGroup>
	        {#each Object.keys(runStatuses) as s, i}
	            <ListGroupItem>{runStatuses[s]}</ListGroupItem>
	        {/each}
		</ListGroup>
	</Container>
</Container>

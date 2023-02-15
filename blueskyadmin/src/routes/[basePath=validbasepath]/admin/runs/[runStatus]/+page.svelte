<script>
	import { Container, Nav, NavItem, NavLink, Table } from 'sveltestrap';
	import { runStatuses } from '$lib/run-status'

  /** @type {import('./$types').PageData} */
  export let data;

</script>


<Container fluid="true">
	<Nav>
		{#each Object.keys(runStatuses) as s, i}
		  <NavItem>
		    <NavLink href={s}>{runStatuses[s]}</NavLink>
		  </NavItem>
		{/each}
	</Nav>
	<h1>{runStatuses[data.runStatus]}</h1>
	{#if data.error}
        {data.error}
    {:else}
		<div>TODO....</div>
	{/if}
</Container>

<script>
	import { Table, Nav, NavItem, NavLink  } from 'sveltestrap';
	import { reverseRunStatusMappings } from '$lib/run-status'

  /** @type {import('./$types').PageData} */
  export let data;

  const apiUrl = data.basePath
  const runs = [] // TODO: fetch
</script>


<div>
	<Nav>
		{#each Object.keys(reverseRunStatusMappings) as s, i}
		  <NavItem>
		    <NavLink href={s}>{reverseRunStatusMappings[s]}</NavLink>
		  </NavItem>
		{/each}
	</Nav>

	<h1>Runs in state '{reverseRunStatusMappings[data.runStatus]}'</h1>

	<div>TODO....</div>
</div>
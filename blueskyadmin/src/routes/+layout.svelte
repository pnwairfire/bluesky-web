<script>
	import Header from './Header.svelte';
	import './styles.css';

	/** @type {import('./$types').LayoutData} */
	export let data;

	data.basePath
</script>

<div class="app">
	<Header basePath={data.basePath} />

	<main>
		<slot />
	</main>

	<!--<footer>...</footer> -->
</div>


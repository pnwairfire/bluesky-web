<script>
	import Header from './Header.svelte';
	import './styles.css';

	/** @type {import('./$types').LayoutData} */
	export let data;
</script>

<div class="app">
	<Header pathname={data.pathname} />

	<main>
		<slot />
	</main>

	<!--<footer>...</footer> -->
</div>


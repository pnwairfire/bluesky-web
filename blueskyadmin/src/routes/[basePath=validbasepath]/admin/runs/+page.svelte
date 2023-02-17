<script>
    import RunsPage from '$lib/components/runs-page.svelte';

    /** @type {import('./$types').PageData} */
    export let data;
</script>


<RunsPage data={data} />
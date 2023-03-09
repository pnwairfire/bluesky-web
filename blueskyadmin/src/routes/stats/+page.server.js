/* The data load has to be done on the servier because the public API
   doesn't support CORS requests.
 */
import { queryStats } from '$lib/runs'

/** @type {import('./$types').PageServerLoad} */
export async function load({ fetch, params, route, url }) {
    try {
        const runId = url.searchParams.get('runId')
        const stats = await queryStats(fetch, runId)
        console.log(stats)
        return { stats }
    } catch(error) {
        console.error(`Error in load loading stats information: ${error}`);
        return {error}
    }
}

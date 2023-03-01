/* The data load has to be done on the servier because the public API
   doesn't support CORS requests.
 */
import { PUBLIC_API_URL } from '$env/static/public';

/** @type {import('./$types').PageServerLoad} */
export async function load({ fetch, params, route, url }) {
    const apiUrl = `${PUBLIC_API_URL}/runs/stats/monthly`
    console.log(`Fetching from ${apiUrl}`)

    try {
        const res = await fetch(apiUrl, {mode:"no-cors"});
        const stats = await res.json();
        return { stats }
    } catch(error) {
        console.error(`Error in load loading stats information: ${error}`);
        return {error}
    }
}

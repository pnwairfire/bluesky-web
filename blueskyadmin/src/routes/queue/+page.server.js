/* The data load has to be done on the servier because the public API
   doesn't support CORS requests.
 */
import { PUBLIC_API_URL } from '$env/static/public';

const publicApiUrlNoSlash = PUBLIC_API_URL.replace(/\/$/, '')

/** @type {import('./$types').PageServerLoad} */
export async function load({ fetch, params, route, url }) {
    const apiUrl = `${publicApiUrlNoSlash}/queue`
    console.log(`Fetching from ${apiUrl}`)

    try {
        const res = await fetch(apiUrl, {mode:"no-cors"});
        const queueInfo = await res.json();
        return { queueInfo }
    } catch(error) {
        console.error(`Error in load loading queue information: ${error}`);
        return {error}
    }
}

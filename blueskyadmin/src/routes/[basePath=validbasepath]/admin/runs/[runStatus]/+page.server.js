/* The data load has to be done on the servier because the public API
   doesn't support CORS requests.
 */

import { error } from '@sveltejs/kit';
import { runStatuses } from '$lib/run-status'
import { PUBLIC_API_URL } from '$env/static/public';

const limit = 20

/** @type {import('./$types').PageServerLoad} */
export async function load({ fetch, params, route, url }) {
  console.log('url', url)
  const runStatus = params.runStatus

  if (runStatuses[runStatus]) {
    let apiUrl = `${PUBLIC_API_URL}/runs/${runStatus}?limit=${limit}`
    if (params.page)
      apiUrl = `${apiUrl}?offset=${params.page * limit}`
    console.log(`Fetching from ${apiUrl}`)

    try {
      const res = await fetch(apiUrl, {mode:"no-cors"});
      const runsData = await res.json();
      return { runStatus, runsData}
    } catch(error) {
      console.error(`Error in load loading queue information: ${error}`);
      return { error, runStatus }
    }
  }
  throw error(404, 'Not found');
}

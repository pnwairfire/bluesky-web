/* The data load has to be done on the servier because the public API
   doesn't support CORS requests.
 */

import { error } from '@sveltejs/kit';
import { runStatuses } from '$lib/run-status'
import { limit, queryRuns } from '$lib/runs'


/** @type {import('./$types').PageServerLoad} */
export async function load({ fetch, params, route, url }) {
  const basePath = params.basePath
  try {
    let page = url.searchParams.get('page')
    const offset = page * limit
    page = page ? parseInt(page) : 0
    const runsData = queryRuns(fetch, page, offset)
    console.log(runsData)
    return { basePath, runsData, page, limit, offset}
  } catch(error) {
    console.error(`Error in load loading queue information: ${error}`);
    return { basePath, error }
  }
}

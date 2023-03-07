/* The data load has to be done on the servier because the public API
   doesn't support CORS requests.
 */

import { error } from '@sveltejs/kit';
import { runStatuses } from '$lib/run-status'
import { limit, queryRuns } from '$lib/runs'


/** @type {import('./$types').PageServerLoad} */
export async function load({ fetch, params, route, url }) {
  return await loadData(params, url, fetch)
}

async function loadData(params, url, fetch) {
  //console.log('url', url)
  const runStatus = params.runStatus

  if (!runStatus || runStatuses[runStatus]) {
    try {
      let page = url.searchParams.get('page')
      const offset = page * limit
      page = page ? parseInt(page) : 0
      const runId = url.searchParams.get('runId')
      const runsData = queryRuns(fetch, page, offset, runStatus, runId)
      console.log(runsData)
      return { runStatus, runsData, page, limit, offset, runId}
    } catch(error) {
      console.error(`Error in load loading queue information: ${error}`);
      return { runStatus, error }
    }
  }
  throw error(404, 'Not found');
}
/* The data load has to be done on the servier because the public API
   doesn't support CORS requests.
 */

import { error } from '@sveltejs/kit';
import { runStatuses } from '$lib/run-status'
import { limit, queryRuns } from '$lib/runs'


/** @type {import('./$types').PageServerLoad} */
export async function load({ fetch, params, route, url }) {
  //console.log('url', url)
  const basePath = params.basePath
  const runStatus = params.runStatus

  if (!runStatus || runStatuses[runStatus]) {
    try {
      let page = url.searchParams.get('page')
      const offset = page * limit
      page = page ? parseInt(page) : 0
      const runId = url.searchParams.get('runId')
      const runsData = queryRuns(fetch, page, offset, runStatus, runId)
      console.log(runsData)
      return { runStatus, basePath, runsData, page, limit, offset, runId}
    } catch(error) {
      console.error(`Error in load loading queue information: ${error}`);
      return { runStatus, basePath, error }
    }
  }
  throw error(404, 'Not found');
}

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

  if (runStatuses[runStatus]) {
    try {
      let page = url.searchParams.get('page')
      const offset = page * limit
      page = page ? parseInt(page) : 0
      const runsData = queryRuns(fetch, page, offset, runStatus)
      console.log(runsData)
      return { runStatus, basePath, runsData, page, limit, offset}
    } catch(error) {
      console.error(`Error in load loading queue information: ${error}`);
      return { runStatus, basePath, error }
    }
  }
  throw error(404, 'Not found');
}

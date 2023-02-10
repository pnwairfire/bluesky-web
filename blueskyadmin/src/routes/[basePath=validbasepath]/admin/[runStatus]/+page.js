import { error } from '@sveltejs/kit';
import { statuses } from '$lib/run-status'

/** @type {import('./$types').PageLoad} */
export function load({ params, route, url }) {

  if (params.runStatus === statuses.Enqueued) {
    //const url =
    const runs = [] // TODO: fetch
    return {
      params: params,
      route: route,
      url: url,
      runStatus: params.runStatus,
      runs: runs
    }
  }
  throw error(404, 'Not found');
}

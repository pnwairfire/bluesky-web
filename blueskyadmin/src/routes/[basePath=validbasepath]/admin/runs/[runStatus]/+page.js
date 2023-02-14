import { error } from '@sveltejs/kit';
import { translateRunStatus } from '$lib/run-status'

/** @type {import('./$types').PageLoad} */
export function load({ params, route, url }) {
  console.log('url', url)
  const runStatus = translateRunStatus(params.runStatus)

  if (runStatus) {
    return {
      url: url,
      basePath: params.basePath,
      runStatus: params.runStatus,
    }
  }
  throw error(404, 'Not found');
}

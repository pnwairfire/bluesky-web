import { redirect } from '@sveltejs/kit';
import { base } from '$app/paths';
 
/** @type {import('./$types').LayoutServerLoad} */
export function load({ locals, params }) {
  throw redirect(307, `${base}/runs`);
}

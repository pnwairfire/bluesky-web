import { redirect } from '@sveltejs/kit';
 
/** @type {import('./$types').LayoutServerLoad} */
export function load({ locals, params }) {
  throw redirect(307, `/bluesky-web/admin/runs`);
}

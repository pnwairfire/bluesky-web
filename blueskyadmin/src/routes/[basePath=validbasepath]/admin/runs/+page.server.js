import { redirect } from '@sveltejs/kit';
 
/** @type {import('./$types').LayoutServerLoad} */
export function load({ locals, params }) {
  if (!locals.user) {
    throw redirect(307, `/${params.basePath}/admin/runs/enqueued`);
  }
}
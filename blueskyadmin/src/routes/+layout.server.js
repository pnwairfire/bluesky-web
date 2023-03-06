/** @type {import('./$types').LayoutServerLoad} */
export async function load({params, url}) {
  return {
    pathname: url.pathname
  };
}
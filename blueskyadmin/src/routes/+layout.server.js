/** @type {import('./$types').LayoutServerLoad} */
export async function load({params, url}) {
  return {
    basePath: params.basePath,
    pathname: url.pathname
  };
}
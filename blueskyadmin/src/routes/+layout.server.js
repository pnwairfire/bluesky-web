/** @type {import('./$types').LayoutServerLoad} */
export async function load({params}) {
  return {
    basePath: params.basePath
  };
}
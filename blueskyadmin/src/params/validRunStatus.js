/** @type {import('@sveltejs/kit').ParamMatcher} */
export function match(param) {
  const t = /^[^/]+$/.test(param);
  console.log(`param: ${param}, t: ${t}`, )
  return t
}

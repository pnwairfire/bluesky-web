/** @type {import('@sveltejs/kit').ParamMatcher} */
export function match(param) {
  return /^bluesky-web.*$/.test(param);
}

import { dev } from '$app/environment';

// we don't need any JS on this page, though we'll load
// it in dev so that we get hot module replacement
export const csr = dev;

// We can't pre-render, since the route has the 'basePath' slug.
//export const prerender = true;

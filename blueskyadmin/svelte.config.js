import adapter from '@sveltejs/adapter-node';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter(),
		paths: {
			// `base` must starts with a slash but not end with one.
			base: '/bluesky-web/admin'
		}
	}
};

export default config;

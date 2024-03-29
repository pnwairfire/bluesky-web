import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		host: '0.0.0.0',
 		port: 8882,
 		strictPort: false,
	},
	preview: {
 		host: '0.0.0.0',
 		port: 8882,
		strictPort: false,
	},
	ssr: {
		noExternal: ['chart.js'],
	},
});

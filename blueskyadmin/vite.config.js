import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
 	server: {
 		port: 8882,
 		strictPort: false,
 	},
 	preview: {
 		port: 8882,
		strictPort: false,
 	}
});

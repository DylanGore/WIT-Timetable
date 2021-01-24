import vue from '@vitejs/plugin-vue';

/**
 * @type {import('vite').UserConfig}
 */

export default ({ command, mode }) => {
    if (command === 'build') {
        return {
            plugins: [vue()],
            build: {
                base: '/dist/',
                outDir: '../dist',
                emptyOutDir: true
            }
        };
    } else {
        return {
            plugins: [vue()]
        };
    }
};

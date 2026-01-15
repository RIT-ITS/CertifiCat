import { resolve } from 'node:path'
import { defineConfig } from 'vite'
import { visualizer } from 'rollup-plugin-visualizer';
import importGraph from 'vite-plugin-import-graph'

function moduleIdToChunks(id) {
    const nodules = "node_modules";
    
    const easyMdeBundle = [
        nodules + '/easymde/',
        nodules + '/codemirror/',
        nodules + '/codemirror-spell-checker/'
    ]

    for(const module of easyMdeBundle) {
        if(id.includes(module)) {
            return "easymde";
        }
    }

    if (id.includes(nodules)) {
        return "vendor";
    }

    return null;
}

let base = 'https://certificat-dev.localhost';
switch(process.env.NODE_ENV) {
    case 'development':
        base = 'https://certificat-dev.localhost';
        break;
    case 'production':
        base = '/static/certificat.vite/';
        break;  
}


export default defineConfig({
    base: base,
    publicDir: false,
    server: {
        port: 5173,
        strictPort: true,
        host: true,
        cors: {
            origin: ['https://certificat.dev.localhost']
        },
        allowedHosts: ['certificat-vite.dev.localhost'],
        hmr: {
            clientPort: 443,
            protocol: 'wss',
            host: 'certificat-vite.dev.localhost'
        }
    },
    plugins: [
        importGraph({
            filename: 'import-graph.json',
            absoluteModuleIds: false,
            usePrefix: false,
        }),
        visualizer({
            filename: "bundle-report.html", // Name of the generated file
        }),
    ],
    build: {
        manifest: 'manifest.json',
        rollupOptions: {
            input: {
                app: resolve(__dirname, 'src/app.ts'),
                easymde: resolve(__dirname, 'src/easymde.ts')
            },
            output: {
                hoistTransitiveImports: false,
                inlineDynamicImports: false,
                manualChunks: moduleIdToChunks
            }

        },
        outDir: '../certificat/modules/html/static/certificat.vite',
        emptyOutDir: true,
    }
});
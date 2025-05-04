const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
const staticPath = path.resolve("../certificat/modules/html/static/");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const TerserPlugin = require("terser-webpack-plugin");

module.exports = (env) => {
    return {
        mode: env.production ? "production" : "development",
        entry: {
            app: './src/app.ts',
            vendor: './src/vendor.ts',
            easymde: './src/easymde.ts'
        },
        devtool: env.production ? 'cheap-module-source-map' : 'inline-source-map',
        module: {
            rules: [
                {
                    test: /\.tsx?$/,
                    use: 'ts-loader',
                    exclude: /node_modules/,
                },
                {
                    test: /\.s[ac]ss$/i,
                    use: [
                        // Creates `style` nodes from JS strings
                        MiniCssExtractPlugin.loader,
                        // Translates CSS into CommonJS
                        "css-loader",
                        // Compiles Sass to CSS
                        {
                            loader: "sass-loader",
                            options: {
                                // Prefer `dart-sass`
                                implementation: require("sass"),
                            },
                        },
                    ],
                },
            ],
        },
        optimization: {
            usedExports: true,
            splitChunks: {
                cacheGroups: {
                    commons: {
                        test(mod/* , chunk */) {
                            if(!mod.context) return;

                            // Only node_modules are needed
                            if (!mod.context.includes('node_modules')) {
                              return false;
                            }
                            
                            // Splitchunks will add these to the cache file and I want to control them
                            // more granularly. 
                            //
                            // codemirror + easymde are a package deal and are split out separately
                            //
                            // highlight.js is included in a separate entrypoint and only the specific
                            // functions we need are loaded. Then the rest of the languages are tree-shaken
                            if (['codemirror', 'easymde', 'highlight.js'].some(str => mod.context.includes(str))) {
                              return false;
                            }
                            return true;
                        },
                        name: 'cache',
                        chunks: 'all',
                    },
                },
            },
            minimize: true,
            minimizer: [new TerserPlugin()],
        },
        resolve: {
            extensions: ['.tsx', '.ts', '.js'],
        },
        output: {
            filename: "[name].[chunkhash].js",
            hashFunction: 'md5',
            hashDigestLength: 10,
            path: path.join(staticPath, "certificat.bundle"),
            clean: true
        },
        plugins: [
            new BundleTracker({ path: staticPath, filename: 'webpack-stats.json' }),
            new MiniCssExtractPlugin({
                // Options similar to the same options in webpackOptions.output
                // both options are optional
                filename: "[name].[contenthash].css",
                chunkFilename: "[id].css",
            }),
        ]
    };
}
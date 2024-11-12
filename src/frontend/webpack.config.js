const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
const staticPath = path.resolve("../certificat/modules/html/static/");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");



module.exports = (env) => {
    return {
        mode: env.production ? "production" : "development",
        entry: './src/index.ts',
        devtool: 'inline-source-map',
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
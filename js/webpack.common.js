const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = {
    entry: './src/index.ts',
    plugins: [
        new HtmlWebpackPlugin({
            title: 'Bathymetry Preview',
            inject: false,
            templateContent: ({ htmlWebpackPlugin }) => `
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8"/>
                    <title>${htmlWebpackPlugin.options.title}</title>
                    <style>
                        .progress-bar-container {
                            position: absolute;
                            left: 50%;
                            top: 50%;
                            transform: translate(-50%, -50%);
                            width: 100%;
                            height: 100%;
                            background-color: rgba(0, 0, 0, 0.8);
                            display: flex;
                            flex-direction: column;
                            justify-content: center;
                            align-items: center;
                        }
                        #progress-bar {
                            width: 30%;
                            margin-top: 0.5%;
                            height: 2%;
                        }
                        label {
                            color: white;
                            font-size: 2rem;
                        }
                        html,
                        body {
                            overflow: hidden;
                        }
                    </style>
                    ${htmlWebpackPlugin.tags.headTags}
                </head>
                <body>
                    <div class="progress-bar-container">
                        <label for="progress-bar">Loading...</label>
                        <progress id="progress-bar" value="0" max="100"></progress>
                    </div>
                    ${htmlWebpackPlugin.tags.bodyTags}
                </body>
                </html>
                `
        }),
        new CopyWebpackPlugin({
            patterns: [
                { from: 'src/assets', to: 'assets' }
            ]
        })
    ],
    output: {
        filename: 'bundle.js',
        path: path.resolve(__dirname, 'dist'),
        clean: true,
    },
    module: {
        rules: [
            {
                test: /\.(png|svg|jpg|jpeg|gif|hdr)$/i,
                type: 'asset/resource',
            },
            {
                test: /\.tsx?$/,
                use: 'ts-loader',
                exclude: /node_modules/,
            },
        ],
    },
    resolve: {
        extensions: ['.tsx', '.ts', '.js'],
    },
    experiments: {
        topLevelAwait: true,
    }
};
const path = require('path');
const WebpackLiveReloadPlugin = require('webpack-livereload-plugin'); // Импортируем плагин!

module.exports = {
    entry: {
        main: './static/js/app.js',
        formHandler: './static/js/formHandler.js'
    },
    output: {
        filename: '[name].bundle.js',
        path: path.resolve(__dirname, 'static/dist'),
    },
    mode: 'development', // или 'production'
    devtool: 'inline-source-map', // опционально, для отладки
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env']
                    }
                }
            }
        ]
    },
    resolve: {
        modules: [path.resolve(__dirname, 'node_modules')],
    },
    plugins: [
        new WebpackLiveReloadPlugin({
            watch: path.resolve(__dirname, 'static/dist'),
        }),
    ],
};
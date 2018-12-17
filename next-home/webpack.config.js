const path = require('path');
const VueLoaderPlugin = require('vue-loader/lib/plugin')


module.exports = {
    entry: './src/index.js',
    mode: 'development',
    watch: true,
    output: {
        path: path.resolve(__dirname, 'dist'),
        filename: 'all.js'
    },
    resolve: {
        alias: {
            'vue$': 'vue/dist/vue.esm.js' // 'vue/dist/vue.common.js' for webpack 1
        }
    },
    mode: 'development',
    module: {
        rules: [
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader']
            },
            {
                test: /\.vue$/,
                loader: 'vue-loader'
            }
        ]
    },
    plugins: [
        // make sure to include the plugin!
        new VueLoaderPlugin()
    ]

}
;


const path = require('path');

module.exports = {
    entry: './src/index.js',
    mode: 'development',
    output: {
        path: path.resolve(__dirname, '../static/ui/build'),
        filename: 'all.js'
    },
    watch: true,
    module: {
        rules: [{
                test: /\.js$/,
                exclude: /node_modules\//,
                use: [
                    {
                        loader: 'ng-annotate-loader'
                    },
                    {
                         loader : 'babel-loader',
                         options: {
                             presets: ['env']
                         }
                    }
                    ]
            },

        ]
    }

};
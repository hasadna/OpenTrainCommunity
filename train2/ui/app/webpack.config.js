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
            {
                test: /\.scss$/,
                use: [{
                    loader: "style-loader"
                }, {
                    loader: "css-loader"
                }, {
                    loader: "sass-loader",
                    options: {
                        includePaths: [
                            path.resolve(__dirname, "./src/scss")
                        ]
                    }
                }]
            },
            {
                test: /\.(woff|woff2|eot|ttf|otf|png|svg|jpg|gif)$/,
                use: [{
                    loader: "file-loader"
                }]
            }
        ]
    }

};
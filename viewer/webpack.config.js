const path = require('path');

var TSLintPlugin = require('tslint-webpack-plugin');

module.exports = {
  entry: './src/viewer.ts',
  module: {
    rules: [
      {
          test: /\.tsx?$/,
          use: 'ts-loader',
          exclude: /node_modules/
      }, {
          test: /\.css$/,
          use: ['style-loader', 'css-loader']
      }
    ]
  },
  resolve: {
    extensions: [ '.ts', '.js', '.css' ]
  },
  output: {
    filename: 'bundle.js',
    path: __dirname,
    publicPath: ''
  },
  mode: 'production',
  plugins: [
    new TSLintPlugin({
      files: ['./src/**/*.ts']
    })
  ]
};

# RouteExplorer

RouteExplorer is a web UI for exploring OpenTrain data.

## Layout

* `RouteExplorer/`
  * `js/`: JavaScript sources
  * `scss/`: Sass stylesheets
  * `tpls/`: Angular.js templates
  * `img/`: Image assets
  * `dist/`: Compiled files for production, plus their sourcemaps
    * `js/`: Bundled & minified JavaScript
    * `css/`: Bundled & compiled CSS
  * `node_modules/`: Development tools installed by NPM
  * `bower_components/`: Front-end components installed by Bower

## Development

We use [NPM](http://npmjs.org) and [Bower](http://bower.io) to manage
dependencies. Broadly, NPM manages development dependencies like our
Gulp tasks, while Bower manages frontend dependencies like Angular and
Bootstrap.

### NPM and Bower

If you don't have npm on your system, get it by installing
[node.js](http://nodejs.org) or [io.js](http://iojs.org).

Then, install all the required dev dependencies with:

```shell
npm install # this will also install bower
bower install
```

### Gulp

We use Gulp to streamline our development tasks.
The default task takes care of generating everything for the first time
and watching the files for changes.

```shell
# gulp

[20:17:24] Starting 'scripts'...
Minifying Scripts...
[20:17:24] Finished 'scripts' after 23 ms
[20:17:24] Starting 'styles'...
Compiling Styles...
[20:17:24] Finished 'styles' after 7.03 ms
[20:17:24] Starting 'watch'...
Gulp is watching for changes...
[20:17:24] Finished 'watch' after 31 ms
[20:17:24] Starting 'default'...
[20:17:24] Finished 'default' after 11 μs
```
You can now hack around as you wish and gulp will regenerate files
in `dist/` as needed.

Other tasks include:
* `gulp scripts` to compile and minify JavaScript sources
* `gulp styles` to compile and minify Sass sources
* `gulp watch` to watch sources for changes and recompile as needed

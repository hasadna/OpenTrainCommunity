# RouteExplorer

RouteExplorer is a web UI for exploring OpenTrain data.

## Dependencies

### Sass

We use Sass for stylesheets.
You'll need Ruby installed on your system. Then:

```shell
gem install sass
./sass-update.sh # run once to generate CSS; see below for development mode
```

### Bower

We use [Bower](http://bower.io) to manage dependencies.
You'll need Node.js installed on your system. Then:

```shell
npm install -g bower
bower install
```

This will download all remaining dependencies.

## Development

### Generating CSS from SCSS

During development, it's handy to watch the `scss` folder so that CSS is automatically generated from SCSS files. A script that does this using the correct load-path is included:

```shell
./sass-watch.cmd # on Windows
./sass-watch.sh # on POSIX environments
```

If you don't plan on modifying any SCSS files, you'll still need to generate the CSS once, by running `sass-update.sh`.

Enjoy!

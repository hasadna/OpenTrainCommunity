# RouteExplorer

RouteExplorer is a web UI for exploring OpenTrain data.

## Dependencies

### Sass

We use Sass for stylesheets.
You'll need Ruby installed on your system. Then:

```shell
gem install sass
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

During development, it's handy to watch the `scss` folder. A script that does this using the correct load-path is included.

```shell
./sass-watch.cmd # on Windows
./sass-watch.sh # on POSIX environments
```

Even if you don't plan on modifying any SCSS files, you'll need to run this once to create the initial CSS files.

Enjoy!

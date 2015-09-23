(function () {
    'use strict';

    var config = {
      scripts: {
        src: 'js/**/*.js',
        out: 'dist/js/',
        map: '.'
      },

      styles: {
        src: 'scss/**/*.scss',
        include: ['bower_components/bootstrap-sass/assets/stylesheets/', 'bower_components/fontawesome/scss'],
        out: 'dist/css/',
        map: '.'
      }
    };

    var gulp = require('gulp'),
        concat = require('gulp-concat'),
        uglify = require('gulp-uglify'),
        sass = require('gulp-sass'),
        sourcemaps = require('gulp-sourcemaps'),
        plumber = require('gulp-plumber');

    gulp.task('scripts', function (){
        console.log('Minifying Scripts...');

        gulp.src(config.scripts.src)
            .pipe(plumber())
            .pipe(sourcemaps.init())
              .pipe(concat('app.js'))
              .pipe(uglify())
            .pipe(sourcemaps.write(config.scripts.map))
            .pipe(gulp.dest(config.scripts.out));
    });

    gulp.task('styles', function () {
        console.log('Compiling Styles...');

        gulp.src(config.styles.src)
            .pipe(plumber())
            .pipe(sourcemaps.init())
              .pipe(sass({ outputStyle: 'compressed', includePaths: config.styles.include }))
                .on('error', sass.logError)
            .pipe(sourcemaps.write(config.styles.map))
            .pipe(gulp.dest(config.styles.out));
    });

    // watch task to check files for changes
    gulp.task('watch', function () {
        console.log('Gulp is watching for changes...');
        gulp.watch(config.scripts.src, ['scripts']);
        gulp.watch(config.styles.src, ['styles']);
    });

    gulp.task('default', ['scripts', 'styles', 'watch']);

}());

const gulp = require('gulp');
const less = require('gulp-less');
const flipper = require('gulp-css-flipper');


gulp.task('style', function () {
    return gulp.src('./style/less/*.less')
        .pipe(less())
        .pipe(flipper())
        .pipe(gulp.dest('./style/dist/'));
});

gulp.task('style:watch', () => {
    gulp.watch(['./style/less/*.less'],
        ['style']);
});

gulp.task('watch',['style:watch']);

gulp.task('default', ['style', 'watch']);




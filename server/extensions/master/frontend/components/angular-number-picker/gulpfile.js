'use strict';

var gulp = require('gulp');

var copyhAuto = function() {
    gulp.src('./angular-number-picker.js').pipe(gulp.dest('./demo/'));
    gulp.src('./angular-number-picker.min.js').pipe(gulp.dest('./demo/'));
};

gulp.task('dev', ['dist'], function(cons) {
    var webserver = require('gulp-webserver');
    copyhAuto();
    gulp.watch('./angular-number-picker.js', function() {
        copyhAuto();
    });

    gulp.src('./demo/')
        .pipe(webserver({
            host: '0.0.0.0',
            port: 8080,
            livereload: true,
            directoryListing: false,
            open: false
        }));

    cons();
});


gulp.task('dist', function() {
    var rename = require('gulp-rename');
    var uglify = require('gulp-uglify');

    return gulp.src('./angular-number-picker.js')
        .pipe(rename({extname: '.min.js'}))
        .pipe(uglify())
        .pipe(gulp.dest('./'));
});

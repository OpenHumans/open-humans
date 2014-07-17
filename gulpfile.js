/*eslint-env node*/

'use strict';

var browserify = require('browserify');
var gulp = require('gulp');
var mainBowerFiles = require('main-bower-files');
var source = require('vinyl-source-stream');

var plugins = require('gulp-load-plugins')();

var paths = {
  js: './static/js/**.js',
  sass: './static/sass/**.sass'
};

gulp.task('lint', function () {
  gulp.src(paths.js)
    .pipe(plugins.eslint())
    .pipe(plugins.eslint.format());
});

gulp.task('bower-install', function () {
  return plugins.bower();
});

gulp.task('bower', ['bower-install'], function () {
  return gulp.src(mainBowerFiles())
    .pipe(gulp.dest('./build/vendor'));
});

gulp.task('browserify', function () {
  return browserify('./static/js/index.js')
      .plugin('minifyify', {
        map: '/static/js/bundle.map.json',
        output: './build/js/bundle.map.json'
      })
      .bundle()
    .pipe(source('bundle.js'))
    .pipe(gulp.dest('./build/js'))
    .pipe(plugins.livereload());
});

gulp.task('sass', function () {
  gulp.src(paths.sass)
    .pipe(plugins.sass())
    .pipe(gulp.dest('./build/css'))
    .pipe(plugins.livereload());
});

gulp.task('watch', function () {
  gulp.watch(paths.js, ['browserify']);
  gulp.watch(paths.sass, ['sass']);
});

gulp.task('default', ['bower', 'browserify', 'sass', 'watch']);

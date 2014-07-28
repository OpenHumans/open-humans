/*eslint-env node*/

'use strict';

var browserify = require('browserify');
var gulp = require('gulp');
var mainBowerFiles = require('main-bower-files');
var mkdirp = require('mkdirp');
var rimraf = require('rimraf');
var source = require('vinyl-source-stream');

var plugins = require('gulp-load-plugins')();

var paths = {
  js: './static/js/**.js',
  sass: './static/sass/**.sass',
  python: '**/*.py'
};

// Clean up files
gulp.task('clean', function (cb) {
  rimraf('./build', cb);
});

// Lint JavaScript code
gulp.task('lint-js', function () {
  return gulp.src(paths.js)
    .pipe(plugins.eslint())
    .pipe(plugins.eslint.format());
});

// Lint Python code
gulp.task('lint-python', function () {
  return gulp.src(paths.python)
    .pipe(plugins.shell([
      'flake8 <%= file.path %>',
      'pylint --reports=no <%= file.path %>'
    ]));
});

gulp.task('lint', ['lint-js', 'lint-python']);

// Ensure bower components are installed
gulp.task('bower-install', function () {
  return plugins.bower();
});

// Collect the main files of the installed bower components
gulp.task('bower', ['bower-install'], function () {
  return gulp.src(mainBowerFiles())
    .pipe(gulp.dest('./build/vendor'));
});

// Browserify, minify, create sourcemaps, bundle, and livereload
gulp.task('browserify', function () {
  mkdirp('./build/js', function (err) {
    if (err) {
      throw err;
    }

    // TODO: We'll eventually have more than one bundle
    return browserify('./static/js/main.js')
        .plugin('minifyify', {
          map: '/static/js/bundle.map.json',
          output: './build/js/bundle.map.json'
        })
        .bundle()
        .on('error', function (err) {
          console.log(err.toString());

          this.emit('end');
        })
      .pipe(source('bundle.js'))
      .pipe(gulp.dest('./build/js'))
      .pipe(plugins.livereload());
  });
});

// Compile sass files into CSS
gulp.task('sass', function () {
  return gulp.src(paths.sass)
    .pipe(plugins.sass())
    .pipe(gulp.dest('./build/css'))
    .pipe(plugins.livereload());
});

// Run browserify on JS changes, sass on sass changes
gulp.task('watch', function () {
  gulp.watch(paths.js, ['browserify']);
  gulp.watch(paths.sass, ['sass']);
  gulp.watch('./bower.json', ['bower']);
});

gulp.task('default', ['bower', 'browserify', 'sass', 'watch']);

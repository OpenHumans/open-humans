/*eslint-env node*/

'use strict';

var path = require('path');

var browserify = require('browserify');
var eventStream = require('event-stream');
var glob = require('glob');
var gulp = require('gulp');
var mainBowerFiles = require('main-bower-files');
var rimraf = require('rimraf');
var source = require('vinyl-source-stream');

var plugins = require('gulp-load-plugins')();

var args = require('yargs').argv;

var paths = {
  js: './static/js/**.js',
  jsEntries: './static/js/*.js',
  sass: './static/sass/**.scss',
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

// Browserify all of our JavaScript entry points
gulp.task('browserify', function () {
  // XXX: I kind of hate this but couldn't figure out how to start the stream
  // with gulp.src and use the filenames it provides.
  var files = glob.sync(paths.jsEntries);

  var tasks = files.map(function (js) {
    var basename = 'bundle-' + path.basename(js, '.js');

    return browserify(js, {debug: true})
        .plugin('minifyify', {
          map: '/static/js/' + basename + '.map.json',
          output: './build/js/' + basename + '.map.json'
        })
        .bundle()
        .on('error', function (err) {
          console.log(err.toString());

          this.emit('end');
        })
      .pipe(source(basename + '.js'))
      .pipe(gulp.dest('./build/js'))
      .pipe(plugins.if(!args.production, plugins.livereload()));
  });

  return eventStream.concat.apply(null, tasks);
});

// Compile sass files into CSS
gulp.task('sass', function () {
  return gulp.src(paths.sass)
    .pipe(plugins.sass())
    .pipe(gulp.dest('./build/css'))
    .pipe(plugins.if(!args.production, plugins.livereload()));
});

// Run browserify on JS changes, sass on sass changes
gulp.task('watch', function () {
  gulp.watch(paths.js, ['browserify']);
  gulp.watch(paths.sass, ['sass']);
  gulp.watch('./bower.json', ['bower']);
});

// Just build the files in ./build
gulp.task('build', ['bower', 'browserify', 'sass']);

// Build, livereload, and watch
gulp.task('default', ['build', 'watch']);

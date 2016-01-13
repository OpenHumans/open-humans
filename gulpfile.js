'use strict';

var _ = require('lodash');
var browserify = require('browserify');
var bundleLogger = require('./gulp/bundle-logger.js');
var glob = require('glob');
var gulp = require('gulp');
var mergeStream = require('merge-stream');
var path = require('path');
var precss = require('precss');
var rimraf = require('rimraf');
var source = require('vinyl-source-stream');
var watchify = require('watchify');

var plugins = require('gulp-load-plugins')();

var args = require('yargs').argv;

var paths = {
  js: [
    './static/js/**.js',
    './**/static/js/**.js'
  ],
  jsEntries: [
    './static/js/*.js',
    './**/static/js/*.js'
  ],
  css: [
    './static/css/**/*.scss',
    '!./static/css/**/_*.scss'
  ],
  python: [
    '**/*.py',
    '!**/migrations/*.py',
    '!./tmp/**/*.py',
    '!./node_modules/**/*.py'
  ],
  bootstrapFiles: [
    './node_modules/bootstrap/dist/css/bootstrap.css',
    './node_modules/bootstrap/dist/css/bootstrap.css.map',
    './node_modules/bootstrap/dist/css/bootstrap-theme.css',
    './node_modules/bootstrap/dist/css/bootstrap-theme.css.map'
  ],
  webshimFiles: [
    './node_modules/webshim/js-webshim/minified/shims/**/*'
  ]
};

// Clean up files
gulp.task('clean', function (cb) {
  rimraf('./build', cb);
});

// Lint JavaScript code
gulp.task('lint-js-eslint', function () {
  return gulp.src(paths.js)
    .pipe(plugins.eslint({
      useEslintrc: true,
      rulePaths: [
        path.join(process.env.HOME, '.eslint')
      ]
    }))
    .pipe(plugins.eslint.format());
});

gulp.task('lint-js-jscs', function () {
  return gulp.src(paths.js)
    .pipe(plugins.jscs());
});

gulp.task('lint-js', ['lint-js-eslint', 'lint-js-jscs']);

// Lint Python code
gulp.task('lint-python', function () {
  var shellOptions = {ignoreErrors: true};

  return gulp.src(paths.python)
    .pipe(plugins.shell([
      'flake8 <%= file.path %> | awk \'$0="flake8: "$0\''
    ], shellOptions))
    .pipe(plugins.shell([
      'pylint --rcfile=.pylintrc -r no -f colorized <%= file.path %> ' +
        '--msg-template "{C}: {path}:{line}:{column} {msg} ({symbol})" ' +
        '| awk \'$0="pylint: "$0\''
    ], shellOptions))
    .pipe(plugins.shell([
      'pep257 <%= file.path %> 2>&1 | awk \'$0="pep257: "$0\''
    ], shellOptions));
});

gulp.task('lint', ['lint-js', 'lint-python']);

gulp.task('bootstrap-files', function () {
  return gulp.src(paths.bootstrapFiles)
    .pipe(gulp.dest('./build/vendor'));
});

gulp.task('webshim-files', function () {
  return gulp.src(paths.webshimFiles)
    .pipe(gulp.dest('./build/vendor/shims'));
});

// Collect Bootstrap and other frontend files
gulp.task('frontend-files', ['bootstrap-files', 'webshim-files']);

function browserifyTask(options) {
  options = options || {};

  // XXX: I kind of hate this but couldn't figure out how to start the stream
  // with gulp.src and use the filenames it provides.
  var files = _.reduce(paths.jsEntries, function (allJsEntries, jsEntry) {
    return allJsEntries.concat(glob.sync(jsEntry));
  }, []);

  files = _.uniq(files);

  var browserifyOptions = {debug: true};

  if (options.development) {
    // Add watchify args
    _.extend(browserifyOptions, watchify.args);
  }

  var tasks = files.map(function (js) {
    var basename = 'bundle-' + path.basename(js, '.js');
    var output = basename + '.js';

    var bundler = browserify(js, browserifyOptions)
      .plugin('minifyify', {
        map: '/static/js/' + basename + '.map.json',
        output: './build/js/' + basename + '.map.json'
      });

    function bundle() {
      // Log when bundling starts
      bundleLogger.start(output);

      return bundler
        .bundle()
        .on('error', function (err) {
          console.error(err.toString());

          process.exit(1);
        })
        .pipe(source(basename + '.js'))
        .pipe(gulp.dest('./build/js'))
        .pipe(plugins.if(!args.production, plugins.livereload()));
    }

    if (options.development) {
      // Wrap with watchify and rebundle on changes
      bundler = watchify(bundler);

      // Rebundle on update
      bundler.on('update', bundle);

      bundleLogger.watch(output);
    }

    return bundle();
  });

  return mergeStream.apply(gulp, tasks);
}

// Browserify all of our JavaScript entry points
gulp.task('browserify', function () {
  browserifyTask();
});

// Watchify all of our JavaScript entry points
gulp.task('watchify', function () {
  browserifyTask({development: true});
});

gulp.task('postcss', function () {
  return gulp.src(paths.css)
    .pipe(plugins.postcss([precss()]))
    .pipe(plugins.cssnano())
    .pipe(plugins.rename({extname: '.css'}))
    .pipe(gulp.dest('./build/css'))
    .pipe(plugins.if(!args.production, plugins.livereload()));
});

// Run browserify on JS changes, postcss on css changes
gulp.task('watch', function () {
  gulp.watch(paths.css, ['postcss']);
});

gulp.task('livereload', function () {
  plugins.livereload.listen();
});

// Just build the files in ./build
gulp.task('build', ['frontend-files', 'postcss', 'browserify']);

// Build, livereload, and watch
gulp.task('default', ['frontend-files', 'postcss', 'watch', 'watchify', 'livereload']);

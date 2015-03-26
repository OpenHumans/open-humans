'use strict';

var gulpUtil = require('gulp-util');
var prettyHrtime = require('pretty-hrtime');
var startTime;

module.exports = {
  start: function (filepath) {
    startTime = process.hrtime();

    gulpUtil.log('Bundling', gulpUtil.colors.green(filepath) + '...');
  },

  watch: function (bundleName) {
    gulpUtil.log('Watching files required by',
      gulpUtil.colors.yellow(bundleName));
  },

  end: function (filepath) {
    var taskTime = process.hrtime(startTime);
    var prettyTime = prettyHrtime(taskTime);

    gulpUtil.log('Bundled', gulpUtil.colors.green(filepath), 'in',
      gulpUtil.colors.magenta(prettyTime));
  }
};

'use strict';

var $ = require('jquery');

$(function () {
  $("[data-toggle='popover']").popover({html: true, trigger: 'focus'});
});

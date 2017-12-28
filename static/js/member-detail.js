'use strict';

var $ = window.jQuery;

$(function () {
  $('[data-toggle="popover"]').popover({html: true, trigger: 'focus'});
});

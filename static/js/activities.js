'use strict';

var $ = require('jquery');

// From example code here: http://api.jquery.com/map/
$.fn.equalizeHeights = function () {
  var maxHeight = this.map(function (i, e) {
    return $(e).height();
  }).get();

  return this.height(Math.max.apply(this, maxHeight));
};

$(function () {
  $("[data-toggle='popover']").popover({html: true, trigger: 'focus'});
  $('.activities-text-block').equalizeHeights();
});

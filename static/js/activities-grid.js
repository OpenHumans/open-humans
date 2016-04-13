'use strict';

var $ = window.jQuery = require('jquery');

require('bootstrap');

$(function () {
  $('[data-toggle="popover"]').popover({html: true, trigger: 'focus'});

  $('.grid').imagesLoaded(function () {
    $('.grid').isotope({
      itemSelector: '.item',
      layoutMode: 'masonry',
      masonry: {
        columnWidth: '.item'
      }
    });
  });
});

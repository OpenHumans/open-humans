'use strict';

var $ = window.jQuery;

$(function () {
  $('[data-toggle="popover"]').popover({html: true, trigger: 'focus'});

  var $grid = $('.grid').isotope({
    itemSelector: '.item',
    layoutMode: 'masonry',
    masonry: {
      columnWidth: '.col-md-4',
      percentPosition: true
    }
  });

  $('.grid').imagesLoaded(function () {
    $('.grid').isotope('layout');
  });

});

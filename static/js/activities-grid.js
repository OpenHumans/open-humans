'use strict';

var $ = window.jQuery = require('jquery');
var _ = require('lodash');

require('bootstrap');

$(function () {
  $('[data-toggle="popover"]').popover({html: true, trigger: 'focus'});

  $('.grid').imagesLoaded(function () {
    var $grid = $('.grid').isotope({
      getSortData: {
        name: '.name'
      },
      itemSelector: '.item',
      layoutMode: 'masonry',
      masonry: {
        columnWidth: '.col-md-4',
        percentPosition: true
      }
    });

    $grid.isotope({sortBy: 'name'});

    $('.show-all button').click(function () {
      $grid.isotope({filter: '*'});
    });

    // TODO: improve handling of connected/not connected
    $('.filters button').click(function () {
      $(this).toggleClass('selected');

      var filters = $.map($('.filters .selected'), function (el) {
        return $(el).attr('data-filter');
      }).join('');

      $grid.isotope({filter: filters});
    });
  });
});

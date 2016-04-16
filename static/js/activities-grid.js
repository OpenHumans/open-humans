'use strict';

var $ = window.jQuery = require('jquery');

require('bootstrap');

$(function () {
  $('[data-toggle="popover"]').popover({html: true, trigger: 'focus'});

  $('.grid').imagesLoaded(function () {
    var $grid = $('.grid').isotope({
      itemSelector: '.item',
      layoutMode: 'masonry',
      masonry: {
        columnWidth: '.col-md-4',
        percentPosition: true
      }
    });

    var filter;

    $grid.on('arrangeComplete', function (event, filteredItems) {
      if (!filteredItems.length) {
        $('.filter-empty[data-filter="' + filter + '"').show();
      }
    });

    $('.filters button').click(function () {
      $('.filters button').removeClass('selected');
      $(this).addClass('selected');

      filter = $(this).attr('data-filter');

      $('.filter-empty').hide();

      $('.filter-description').hide();
      $('.filter-description[data-filter="' + filter + '"').show();

      $grid.isotope({filter: filter});
    });

    $('.filters button[data-filter="*"]').click();
  });
});

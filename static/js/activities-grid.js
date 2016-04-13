'use strict';

var $ = window.jQuery = require('jquery');

require('bootstrap');

$(function () {
  $('[data-toggle="popover"]').popover({html: true, trigger: 'focus'});

  $('.grid').imagesLoaded(function () {
    var $grid = $('.grid').isotope({
      getSortData: {
        name: function (el) {
          return $(el).find('.name').text().toLowerCase();
        }
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
      $('.filters button').removeClass('selected');

      $grid.isotope({filter: '*'});
    });

    function filter(button) {
      $(button).toggleClass('selected');

      var filters = $.map($('.filters .selected'), function (el) {
        return $(el).attr('data-filter');
      }).join('');

      $grid.isotope({filter: filters});
    }

    $('.filters[data-filter-group="labels"] button').click(function () {
      filter(this);
    });

    $('.filters[data-filter-group="connection-status"] button')
      .click(function () {
        if (!$(this).hasClass('selected')) {
          $('.filters[data-filter-group="connection-status"] button')
            .removeClass('selected');
        }

        filter(this);
      });
  });
});

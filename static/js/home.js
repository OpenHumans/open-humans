'use strict';

var $ = require('jquery');

function getHashFilter() {
  var matches = location.hash.match(/filter=([^&]+)/i);
  var filter = matches && matches[1];

  return (filter && decodeURIComponent(filter)) || '*';
}

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

  function onHashchange() {
    var filter = getHashFilter();

    $('.filters button').removeClass('selected');
    $('.filters button[data-filter="' + filter + '"]').addClass('selected');

    $('.filter-empty').hide();

    $('.filter-description').hide();
    $('.filter-description[data-filter="' + filter + '"]').show();

    $grid.isotope({filter: filter});

    var filteredItems = $('.grid ' + filter);

    if (!filteredItems.length) {
      $('.filter-description').hide();
      $('.filter-empty[data-filter="' + getHashFilter() + '"]').show();
    }
  }

  $('.filters button').click(function () {
    location.hash = 'filter=' +
      encodeURIComponent($(this).attr('data-filter'));
  });

  $(window).on('hashchange', onHashchange);

  onHashchange();
});

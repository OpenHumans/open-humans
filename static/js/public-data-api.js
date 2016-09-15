'use strict';

var $ = window.jQuery = require('jquery');

require('select2/dist/js/select2.full.min.js');

$.fn.select2.defaults.set('theme', 'bootstrap');

$(function () {
  var $sourceSearch = $('#source-search').select2({
    placeholder: 'Select an activity',
  });

  $sourceSearch.on('select2:select', function () {
    var url = 'https://www.openhumans.org/api/public-data/?source=' +
      $sourceSearch.val();

    $('#source-url').html('<a href="' + url + '">' + url + '</a>');
  });
});

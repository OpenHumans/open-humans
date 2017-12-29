'use strict';

var $ = require('jquery');

require('select2/dist/js/select2.full.js')($);

$(function () {
  var $sourceSearch = $('#source-search').select2({
    placeholder: 'Select an activity',
    theme: 'bootstrap'
  });

  $sourceSearch.on('select2:select', function () {
    var url = 'https://www.openhumans.org/api/public-data/?source=' +
      $sourceSearch.val();

    $('#source-url').html('<a href="' + url + '">' + url + '</a>');
  });
});

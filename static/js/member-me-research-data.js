'use strict';

var $ = require('jquery');

var url = document.location.toString();

$(function () {
  $("[data-toggle='popover']").popover({html: true, trigger: 'focus'});

  // So we can link to this modal directly from the 'activities' page.
  if (url.match('#add-data-23andme-modal')) {
    $('#add-data-23andme-modal').removeClass('fade').modal('show');
  }
});

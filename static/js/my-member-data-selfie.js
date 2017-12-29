/*global SELFIE_ACKNOWLEDGE_URL:true, SELFIE_SHOW_MODAL:true*/

'use strict';

var enableCsrf = require('./lib/enable-csrf.js');
var publicSharingToggle = require('./lib/public-sharing-toggle.js');

require('bootstrap');

enableCsrf($);

$(function () {
  $('[data-toggle="popover"]').popover({html: true, trigger: 'focus'});

  publicSharingToggle();

  $('.delete-button').click(function (e) {
    e.preventDefault();
  });

  if (!SELFIE_SHOW_MODAL) {
    return;
  }

  $('#data-selfie-modal').modal({
    keyboard: false,
    backdrop: 'static'
  });

  $('#continue').click(function (e) {
    e.preventDefault();

    $('#data-selfie-modal').modal('hide');

    $.post(SELFIE_ACKNOWLEDGE_URL);
  });
});

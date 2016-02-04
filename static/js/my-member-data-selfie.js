/*global SELFIE_ACKNOWLEDGE_URL:true, SELFIE_SHOW_MODAL:true*/

'use strict';

var enableCsrf = require('./lib/enable-csrf.js');
var $ = window.jQuery = require('jquery');

require('bootstrap');

enableCsrf($);

$(function () {
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

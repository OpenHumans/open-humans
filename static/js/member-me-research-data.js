'use strict';

var publicSharingToggle = require('./lib/public-sharing-toggle.js');

require('bootstrap');

$(function () {
  $('[data-toggle="popover"]').popover({html: true, trigger: 'focus'});

  publicSharingToggle();

  $('form.delete-selfie-file').on('click', 'input[type=submit]', function (e) {
    e.preventDefault();

    var $form = $(this).parent();
    var formUrl = $form.attr('action');

    var self = this;

    $.post(formUrl, $form.serialize(), function () {
      var $tr = $(self).parents('tr').eq(0);

      $tr.hide('slow', function () {
        $tr.remove();
      });
    }).fail(function () {
      // fall back to a regular form submission if AJAX doesn't work
      $form.submit();
    });
  });
});

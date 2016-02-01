'use strict';

var $ = window.jQuery = require('jquery');

require('bootstrap');

$(function () {
  $('[data-toggle="popover"]').popover({html: true, trigger: 'focus'});

  // AJAX toggling for public data sharing
  $('form.toggle-sharing').on('click', 'input[type=submit]', function (e) {
    e.preventDefault();

    var $form = $(this).parent();
    var formUrl = $form.attr('action');

    var isPublic = $(this).siblings('input[name=public]').val() === 'True';

    var newState = isPublic ? 'False' : 'True';
    var newValue = isPublic ? 'Stop public sharing' : 'Share publicly';

    var self = this;

    $.post(formUrl, $form.serialize(), function () {
      $(self).val(newValue);
      $(self).siblings('input[name=public]').val(newState);
    }).fail(function () {
      // fall back to a regular form submission if AJAX doesn't work
      $form.submit();
    });
  });

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

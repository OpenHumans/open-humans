'use strict';

module.exports = function () {
  // AJAX toggling for public data sharing
  $('form.toggle-sharing').on('click', 'button[type=submit]', function (e) {
    e.preventDefault();

    var self = this;
    $(self).html("Updating...");
    $(self).prop("disabled", true);

    var $form = $(this).parent();
    var formUrl = $form.attr('action');

    var isPublic = $(this).siblings('input[name=public]').val() === 'True';

    var newState = isPublic ? 'False' : 'True';
    var newValue = isPublic ? 'Stop public sharing' : 'Share publicly';

    $.post(formUrl, $form.serialize(), function () {
      $(self).html(newValue);
      $(self).removeAttr('disabled')
      $(self).siblings('input[name=public]').val(newState);
    }).fail(function () {
      // fall back to a regular form submission if AJAX doesn't work
      $form.submit();
    });
  });
};

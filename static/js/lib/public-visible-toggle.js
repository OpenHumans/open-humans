'use strict';

module.exports = function () {
  // AJAX toggling for public data visibility
  $('form.toggle-visibility').on('click', 'button[type=submit]', function (e) {
    e.preventDefault();

    var self = this;
    $(self).html("Updating...");
    $(self).prop("disabled", true);

    var $form = $(this).parent();
    var formUrl = $form.attr('action');

    var isVisible = $(this).siblings('input[name=visible]').val() === 'True';

    var newState = isVisible ? 'False' : 'True';
    var newValue = isVisible ? 'Visible' : 'Hidden';

    $.post(formUrl, $form.serialize(), function () {
      $(self).html(newValue);
      $(self).removeAttr('disabled')
      $(self).siblings('input[name=visible]').val(newState);
    }).fail(function () {
      // fall back to a regular form submission if AJAX doesn't work
      $form.submit();
    });
  });
};

'use strict';

$(function () {
  $('#id_password_current').attr('required', '');

  $('#id_password_new').attr('required', '');
  $('#id_password_new_confirm').attr('required', '');

  $('#id_password_new').attr('minlength', '8');
  $('#id_password_new_confirm').attr('minlength', '8');

  $('#id_password_new_confirm').attr('data-parsley-equalto', '#id_password_new');
});

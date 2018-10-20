'use strict';

$(function () {
  $('#id_password').attr('required', '');
  $('#id_password_confirm').attr('required', '');

  $('#id_password').attr('minlength', '8');
  $('#id_password_confirm').attr('minlength', '8');

  $('#id_password_confirm').attr('data-parsley-equalto', '#id_password');
});

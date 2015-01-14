/*globals $:true*/

'use strict';

function csrfSafeMethod(method) {
  // These HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

var csrfToken = $.cookie('csrftoken');

$.ajaxSetup({
  beforeSend: function (xhr, settings) {
    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
      xhr.setRequestHeader('X-CSRFToken', csrfToken);
    }
  }
});

$(function () {
  $('.logout-link').click(function (e) {
    e.preventDefault();

    $.post($(this).attr('href'), function () {
      location.reload();
    });
  });
});

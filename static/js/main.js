'use strict';

var $ = require('jquery');

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

function showModal(modalId) {
  return function (e) {
    // Allow for middle-clicking, control-clicking, and command-clicking
    if (e.isDefaultPrevented() || e.metaKey || e.ctrlKey) {
      return;
    }

    e.preventDefault();

    $(modalId).modal({remote: false});
  };
}

$(function () {
  $('.logout-link').click(function (e) {
    e.preventDefault();

    $.post($(this).attr('href'), function () {
      location.reload();
    });
  });

  // Add these modals with JavaScript rather than data- attributes to prevent
  // AJAX loading of modal content by Bootstrap.
  $('.login-link').click(showModal('#login-modal'));
  $('.signup-link').click(showModal('#signup-modal'));
});

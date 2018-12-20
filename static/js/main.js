/*global webshim:true*/

'use strict';

var enableCsrf = require('./lib/enable-csrf.js');

require('drmonty-garlicjs');
require('webshim');

enableCsrf($);

// Specifically so IE will support the HTML5 form attribute on <input> elements
webshim.setOptions('basePath', '/static/vendor/shims/');
webshim.polyfill('forms');

function parsleyForm(element) {
  return $(element).parsley({
    successClass: 'has-success',
    errorClass: 'has-error',
    trigger: 'change keyup focusout',
    classHandler: function (field) {
      if (field.$element.attr('type') === 'radio') {
        return $('input[type=radio][name=' + field.$element.attr('name') + ']')
          .parents('.radio');
      }

      return field.$element.parents('.form-group');
    },
    errorsContainer: function (field) {
      var $field = field.$element;

      if (field.$element.attr('type') === 'radio') {
        $field = $('input[type=radio][name=' + field.$element.attr('name') +
          ']:last').parent().parent();

        return $('<span></span>').insertAfter($field);
      }

      if (field.$element.parent('.input-group')) {
        $field = field.$element.parent('.input-group');
      }

      return $('<span></span>').insertAfter($field);
    },
    errorsWrapper: '<span class="help-block"></span>',
    errorTemplate: '<div></div>'
  });
}

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

function storeRedirect(){
  console.log('In storeRedirect!');
  var location = window.location.href;
  console.log(location);

  // Make a POST, but not asynchronously!
  $.ajax({ type: 'POST',
           url: '/account/storeredirect/',
           data: {next_url: location},
           success: function(){},
           async:false });
}

$(function () {
  $('[rel=persist]').garlic();

  parsleyForm('form');

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

  // POST current URL to be stored as a redirect link upon login/signup
  $('.redirect-storage-link').click(storeRedirect);
});

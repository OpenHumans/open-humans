'use strict';

var cancelNavigation = require('./lib/cancel-navigation.js');
var $ = window.jQuery;

cancelNavigation('#process-file');

window.dropzoneOptions = {
  customInit: function () {
    this.on('success', function () {
      $('#upload-file-first').hide();
      $('#process-file').show();
    });
  }
};

$(function () {
  $('#upload-file-first').click(function (e) {
    e.preventDefault();
  });
});

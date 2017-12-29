'use strict';

var cancelNavigation = require('./lib/cancel-navigation.js');

cancelNavigation('#process-file');

window.dropzoneOptions = {
  maxFiles: 1,
  maxFilesize: 8192,
  addRemoveLinks: true,

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

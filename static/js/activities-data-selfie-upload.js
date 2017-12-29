'use strict';

var cancelNavigation = require('./lib/cancel-navigation.js');

cancelNavigation('#go-to-data-selfie');

window.dropzoneOptions = {
  addRemoveLinks: false,

  maxFilesize: 8192,

  customInit: function () {
    this.on('success', function () {
      $('#upload-file-first').hide();
      $('#go-to-data-selfie').show();
    });
  }
};

$(function () {
  $('#upload-file-first').click(function (e) {
    e.preventDefault();
  });
});

/*global Dropzone:true*/

'use strict';

var $ = window.jQuery;

var message = 'Please wait until your files are finished uploading (or ' +
  'cancel them).';

function filesAreUploading() {
  var dropzone = Dropzone.forElement('#s3upload');

  var files = dropzone.getUploadingFiles();

  return files.length && files.length > 0;
}

module.exports = function (element) {
  $(window).on('beforeunload', function (e) {
    if (filesAreUploading()) {
      e.returnValue = message;

      return message;
    }
  });

  $(function () {
    $(element).click(function (e) {
      if (filesAreUploading()) {
        alert(message);

        e.preventDefault();
      }
    });
  });
};

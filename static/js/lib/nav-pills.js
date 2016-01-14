'use strict';

var $ = window.jQuery = require('jquery');

require('bootstrap');

function updatePill() {
  var url = document.location.toString();

  if (url.match('#')) {
    $('.nav-pills a[href="#' + url.split('#')[1] + '"]').tab('show');
  }
}

module.exports = function () {
  $(function () {
    // Change the hash when a user clicks on a nav-pill link
    $('.nav-pills a, .table-of-contents a').on('click', function (e) {
      window.location.hash = e.target.hash;
    });

    // Show the correct page when the hash changes
    $(window).on('hashchange', function () {
      updatePill();
    });

    updatePill();
  });
};

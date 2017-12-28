'use strict';

var $ = window.jQuery;

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
      e.preventDefault();

      history.pushState({}, '', e.target.hash);

      updatePill();
    });

    // Show the correct page when the hash changes
    $(window).on('popstate', function () {
      updatePill();
    });

    updatePill();
  });
};

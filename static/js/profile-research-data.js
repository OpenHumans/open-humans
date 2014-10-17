/*globals $:true*/

$(function () {
  $("[data-toggle='popover']").popover({html:true, trigger:'focus'});
});

$(function () {
  // JavaScript to enable link to modal
  var url = document.location.toString();

  if (url.match('#')) {
      console.log(url)
    $('#' + url.split('#')[1]).modal('show');
  }
});

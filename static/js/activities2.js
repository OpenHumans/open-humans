'use strict';

var $ = window.jQuery = require('jquery');

require('bootstrap');

$(function () {
  $('[data-toggle="popover"]').popover({html: true, trigger: 'focus'});

  console.log('loading masonry');
  $('.masonry-container').masonry({
    itemSelector: '.item',
    columnWidth: '.item'
  });
});

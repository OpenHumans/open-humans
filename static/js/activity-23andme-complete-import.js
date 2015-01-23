'use strict';

var $ = require('jquery');

$(function () {
  $.ajax({
    type: 'GET',
    url: '/activity/23andme/get-names/',
    success: function (data) {
      if (data.profiles && data.profiles.length < 1) {
        return;
      }

      data.profiles.forEach(function (profile) {
        var $radio = $('<input>')
          .attr({
            type: 'radio',
            name: 'profile_id',
            value: profile.id,
            checked: data.profiles.length === 1
          });

        var $label = $('<label></label>')
          .append($radio)
          .append(' ' + profile.first_name + ' ' + profile.last_name);

        var $div = $('<div></div>')
          .attr('class', 'radio')
          .append($label);

        $('#23andme-list-profiles').append($div);
      });

      $('#load-23andme-waiting').hide();

      $('#23andme-complete-submit').css('visibility', 'visible');
    }
  });
});

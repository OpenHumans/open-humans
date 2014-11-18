/*globals $:true*/

'use strict';

$(function () {

  $.ajax({
    'type': 'GET',
    'url': '/activity/23andme/get-names/',
    'success': function(data) {
      if (data.profiles && data.profiles.length > 0) {
        data.profiles.forEach(function (profile) {
          var $radioElem = $('<input />');
          $radioElem.attr({'type': 'radio',
                           'name': 'profile_id',
                           'value': profile.id});
          if (data.profiles.length === 1) {
              $radioElem.attr('checked', true);
          }
          var $labelElem = $('<label></label>');
          $labelElem.append($radioElem);
          $labelElem.append(profile.first_name + ' ' +
                            profile.last_name);
          var $divElem = $('<div></div>');
          $divElem.attr('class', 'radio');
          $divElem.append($labelElem);
          $('#23andme-list-profiles').append($divElem);
        });
        $('#load-23andme-waiting').hide();
        $('#23andme-complete-submit').css('visibility', 'visible');
      }
    }
  });
});

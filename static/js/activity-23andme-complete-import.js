$(function () {
  var params = {'data_type': '23andme_names'};

  $.ajax({
    'type': 'GET',
    'url': '/json-data/',
    'data': params,
    'success': function(data) {
      if (data.profiles && data.profiles.length > 0) {
        data.profiles.forEach(function (profile) {
          var $radioElem = $('<input />');
          $radioElem.attr({'type' : 'radio',
                           'name' : 'profile_id',
                           'value' : profile.id});
          if (data.profiles.length == 1) {
              $radioElem.attr('checked', true);
          }
          var $labelElem = $('<label></label>');
          $labelElem.append($radioElem);
          $labelElem.append(data.profiles[i].first_name + ' ' +
                            data.profiles[i].last_name);
          var $divElem = $('<div></div>');
          $divElem.attr('class', 'radio');
          $divElem.append($labelElem);
          $("#23andme-list-profiles").append($divElem);
        });
        $("#load-23andme-waiting").hide();
        $("#23andme-complete-submit").css('visibility', 'visible');
      }
    }
  });
}

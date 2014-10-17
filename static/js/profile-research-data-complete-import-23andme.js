$(function () {
    var params = {'data_type': '23andme_names'};

    $.ajax({
        'type': 'GET',
        'url': '/json_data/',
        'data': params,
        'success': function(data) {
            if ('profiles' in data && data['profiles'].length > 0) {
                for (var i = 0; i < data['profiles'].length; i++) {
                    var radio_elem = $('<input />');
                    radio_elem.attr({'type' : 'radio',
                                     'name' : 'profile_id',
                                     'value' : data['profiles'][i]['id']});
                    if (data['profiles'].length == 1) {
                        radio_elem.attr('checked', true);
                    }
                    var label_elem = $('<label></label>');
                    label_elem.append(radio_elem);
                    label_elem.append(data['profiles'][i]['first_name'] + ' ' +
                                      data['profiles'][i]['last_name'])
                    var div_elem = $('<div></div>');
                    div_elem.attr('class', 'radio');
                    div_elem.append(label_elem);
                    console.log(div_elem);
                    $("#23andme_list_profiles").append(div_elem);
                }
                $("#load-23andme-waiting").hide();
                $("#23andme-complete-submit").css('visibility', 'visible');
            }
        }
    });
});

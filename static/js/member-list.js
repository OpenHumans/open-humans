'use strict';

var $ = window.jQuery = require('jquery');

require('select2/dist/js/select2.full.js')($);

function updateQueryStringParam(key, value) {
  var baseUrl = [
    location.protocol,
    '//',
    location.host,
    location.pathname
  ].join('');

  var urlQueryString = document.location.search;
  var newParam = key + '=' + value;
  var params = '?' + newParam;

  // If the "search" string exists, then build params from it
  if (urlQueryString) {
    var keyRegex = new RegExp('([\?&])' + key + '[^&]*');

    // If param exists already, update it
    if (urlQueryString.match(keyRegex) !== null) {
      params = urlQueryString.replace(keyRegex, '$1' + newParam);
    } else { // Otherwise, add it to end of query string
      params = urlQueryString + '&' + newParam;
    }
  }

  window.location.href = baseUrl + params;
}

$(function () {
  $('#member-search').select2({
    ajax: {
      url: '/api/public-data/members/',
      data: function (params) {
        return {
          search: params.term,
          page: params.page
        };
      },
      processResults: function (data) {
        var results = data.results.map(function (member) {
          var text;

          if (member.name) {
            text = member.name + ' (' + member.username + ')';
          } else {
            text = member.username;
          }

          return {
            id: member.id,
            text: text,
            url: member.url
          };
        });

        return {results: results};
      },
      delay: 250
    },
    placeholder: 'Search by username and member name',
    theme: 'bootstrap'
  });

  $('#member-search').on('select2:select', function (e) {
    location.href = e.params.data.url;
  });

  var $sourceSearch = $('#source-search').select2({
    placeholder: 'Filter by activity',
    allowClear: true
  });

  $sourceSearch.on('select2:select', function () {
    updateQueryStringParam('filter', $('#source-search').val());
  });

  $sourceSearch.on('select2:unselecting', function (e) {
    // prevent the select2 dropdown from popping up
    e.preventDefault();

    updateQueryStringParam('filter', '');
  });
});

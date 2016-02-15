#!/usr/bin/env node

'use strict';

var data = require('./production-data.json');

var filtered = data.filter(d => {
  return d.fields.member === 3 ||
         d.fields.username === 'api-administrator' ||
         d.fields.participant === 2 ||
         d.fields.username === 'beau' ||
         (d.model === 'studies.datarequest' &&
          d.fields.study === 1) ||
         (d.fields.researchers &&
          d.fields.researchers.length &&
          d.fields.researchers[0] == 1) ||
         (d.fields.user &&
          d.fields.user.length &&
          d.fields.user[0] === 'beau') ||
         d.model === 'oauth2_provider.application';
}).filter(d => {
  return d.model !== 'admin.logentry' &&
         // Account objects are created automatically
         d.model !== 'account.account' &&
         // EmailAddress objects are created automatically
         d.model !== 'account.emailaddress' &&
         d.model !== 'data_import.testuserdata' &&
         d.model !== 'data_import.newdatafileaccesslog';
});

var tokens = {};
var counter = 0;

function mapToken(token) {
  if (!tokens[token]) {
    tokens[token] = counter++;
  }

  return tokens[token];
}

var mapped = filtered.map(d => {
  if (d.fields.password) {
    d.fields.password = 'pbkdf2_sha256$20000$M8Mz7sghMmn9$fuEYjTTgSLlxwwDt8eZOt3/nyHH0WR9xvZ8CMIMXK84=';
  }

  if (typeof d.fields.about_me !== 'undefined') {
    d.fields.about_me = '## Testing!\n\nTesting.';
  }

  if (d.fields.expires) {
    d.fields.expires = d.fields.expires.replace(/^20\d{2}/, '2020');
  }

  if (d.fields.is_superuser) {
    d.fields.is_superuser = false;
  }

  if (d.fields.is_staff) {
    d.fields.is_staff = false;
  }

  if (d.fields.client_id) {
    d.fields.client_id = `example-id-${mapToken(d.fields.client_id)}`;
  }

  if (d.fields.client_secret) {
    d.fields.client_secret =
      `example-secret-${mapToken(d.fields.client_secret)}`;
  }

  if (d.fields.code) {
    d.fields.code = `example-code-${mapToken(d.fields.code)}`;
  }

  if (d.fields.token) {
    d.fields.token = `example-token-${mapToken(d.fields.token)}`;
  }

  if (d.fields.data && d.fields.data.files) {
    d.fields.data.files = {};
  }

  // make at least one publicdataaccess.is_public = false
  if (d.fields.data_source === 'wildlife' &&
      d.fields.is_public) {
    d.fields.is_public = false;
  }

  if (d.fields.extra_data) {
    var extraData = JSON.parse(d.fields.extra_data);

    if (extraData.access_token) {
      extraData.access_token =
        `example-access-token-${mapToken(extraData.access_token)}`;
    }

    if (extraData.refresh_token) {
      extraData.refresh_token =
        `example-refresh-token-${mapToken(extraData.refresh_token)}`;
    }

    d.fields.extra_data = JSON.stringify(extraData);
  }

  if (d.fields.app_task_params) {
    var params = JSON.parse(d.fields.app_task_params);

    if (params.access_token) {
      params.access_token =
        `example-access-token-${mapToken(params.access_token)}`;
    }

    if (params.file_url) {
      params.file_url = `http://example.com/${mapToken(params.file_url)}`;
    }

    if (params.data && params.data.files) {
      params.data.files = {};
    }

    d.fields.app_task_params = JSON.stringify(params);
  }

  return d;
});

console.log(JSON.stringify(mapped, null, 2));

'use strict';

function hashHandler() {
  // Reset to target tab and pane when loading the page with a hash.
  var url = document.location.toString();

  if (url.match('#')) {
    var panetarget = url.split('#')[1];
    var tabtarget = panetarget + '-tab';

    // Check that the hash isn't referring to a disabled tab.
    var valid_target = $('#' + tabtarget).not('.disabled');

    if (valid_target.length == 1) {
      // Reset to remove existing "active" tab and panel.
      $('#activity-panel-nav .nav-item .nav-link').removeClass('active');
      $('.tab-pane').removeClass('active show');

      // Set target tab and panel to active.
      $('#' + tabtarget).addClass('active');
      $('#' + panetarget).addClass('active show');

      // hack to prevent jumping scroll to the anchor tag on loading
      setTimeout(function() {
        window.scrollTo(0, 0);
      }, 1);
    }
  }
}

/* 20200717: The linkify function is adapted from the JOGL frontend,
   and is distributed under the MIT License:
   https://gitlab.com/JOGL/frontend-v0.1/-/blob/develop/LICENSE */
function linkify(content) {
  // detect links in a text and englobe them with a <a> tag
  const urlRegex = /\b((?:[a-z][\w-]+:(?:\/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}\/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))/gm;
  return content.replace(urlRegex, function (url) {
    const addHttp = url.substr(0, 4) !== 'http' ? 'http://' : '';
    return '<a href="' + addHttp + url + '">' + url + '</a>';
  });
}

function addJoglLinks(content) {
  // detect root-relative href links and prepend the jogl domain
  return content.replace(/(href=")(\/[^"]*)(")/gm, "$1https://app.jogl.io$2$3");
}

function joglNewsItemContent(div, feedItem) {
  // Header
  const creatorImage = feedItem.creator.logo_url;
  const creatorName = feedItem.creator.first_name + ' ' + feedItem.creator.last_name;
  const creatorLink = 'https://app.jogl.io/user/' + feedItem.creator.id;
  const fromLink = 'https://app.jogl.io/' + feedItem.from.object_type + '/' + feedItem.from.object_id;
  var createdAt = new Date(feedItem.created_at);
  var top_div = '<div class="d-flex flex-row mb-2">' +
    '<div><img src="' + creatorImage + '" class="mh-100 img-fluid rounded-circle"></div>' +
    '<div class="pl-3"><a href="' + creatorLink + '" class="h4">' + creatorName + '</a><br>';
  if (feedItem.from.object_type !== 'user') {
    top_div = top_div + '<span class="h5"><a href="' + fromLink + '">' + feedItem.from.object_name + "</a></span><br>";
  }
  top_div = top_div + '<span class="text-muted">' + createdAt.toDateString() +
    '</span></div>' + '</div>';
  div.append(top_div);

  // Content. Add links to bare URLs, and prepend JOGL domains to bare path links.
  var newsContent = linkify(feedItem.content);
  newsContent = addJoglLinks(newsContent);
  div.append('<div style="white-space: pre-wrap; word-break: break-word;">' + newsContent + '</div>');

  // Add news item link.
  const newsURL = 'https://app.jogl.io/post/' + feedItem.id;
  div.append('<a class="btn btn-sm btn-default mt-3" href="' + newsURL + '">Comment on this</a>');

  // Make all links in news items open in a new tab.
  div.find('a').prop('target', "_blank").prop('rel', "noopener");
}

function sortNeeds(N1, N2) {
  // Urgent open needs first, then other open needs, then closed needs.
  // Within each category, most recently updated needs first.
  if (N1.status == "active" && N2.status == "completed") {
    return -1;
  };
  if (N1.status == "completed" && N2.status == "active") {
    return 1;
  };
  if (N1.status == "active" && N2.status == "active") {
    if (N1.is_urgent && !N2.is_urgent) {
      return -1;
    };
    if (!N1.is_urgent && N2.is_urgent) {
      return 1;
    };
  };
  if (Date.parse(N1.updated_at) > Date.parse(N2.updated_at)) { return -1; };
  if (Date.parse(N1.updated_at) < Date.parse(N2.updated_at)) { return 1; };
  return 0;
}

function joglActiveNeedContent(div, needsItem) {
  const needURL = 'https://app.jogl.io/need/' + needsItem.id;
  // header
  div.append('<h4><a href="' + needURL + '">' + needsItem.title + '</a></h4>');

  // Content. Add links to bare URLs, and prepend JOGL domains to bare path links.
  var needsContent = linkify(needsItem.content);
  needsContent = addJoglLinks(needsContent);
  div.append('<div style="white-space: pre-wrap; word-break: break-word;">' + needsContent + '</div>');

  if (needsItem.skills) {
    div.append('<div><h5 class="text-muted mb-1 mt-2">Helpful skills</h5><ul class="jogl-need-skills pl-3" style="list-style-position: inside;"></ul>');
    for (var i = 0; i < needsItem.skills.length; i++) {
      div.find("ul.jogl-need-skills").append('<li>' + needsItem.skills[i] + '</li>');
    }
  }
  div.append('<a class="btn btn-sm btn-default ml-3" href="' + needURL + '">How to help</a>');

  // Make all links in news items open in a new tab.
  div.find('a').prop('target', "_blank").prop('rel', "noopener");
}

function joglCompletedNeedContent(div, needsItem) {
  const needURL = 'https://app.jogl.io/need/' + needsItem.id;
  // header
  div.append('<h4><a href="' + needURL + '">' + needsItem.title + '</a></h4>');

  // Content. Add links to bare URLs, and prepend JOGL domains to bare path links.
  var needsContent = linkify(needsItem.content);
  needsContent = addJoglLinks(needsContent);
  div.append('<div style="white-space: pre-wrap; word-break: break-word;">' + needsContent + '</div>');

  // Make all links in news items open in a new tab.
  div.find('a').prop('target', "_blank").prop('rel', "noopener");
}

function addJogl(joglId) {
  const joglProjectURL = 'https://jogl-backend.herokuapp.com/api/projects/' + joglId + '/';
  $.getJSON(joglProjectURL, function( projData ) {

    // Load news.
    const joglNewsURL = 'https://jogl-backend.herokuapp.com/api/feeds/' + projData.feed_id;
    $.getJSON(joglNewsURL, function( feedData ) {
      if (feedData.length == 0) {
        // "No news" default text.
        $("#jogl-news").append('No news items yet for <a href="' + joglURL + '">this project\'s JOGL page</a>.')

      } else {
        //$("#jogl-news").append(
        //  '<p><em><b>Comment on news items</b> using this activity\'s <a href="https://app.jogl.io/project/' +
        //  joglId + '#news">JOGL project page</a></em></p>');

        // Add news items.
        var infoTopNews = null; // populate top project news item for info tab
        for (var i = 0; i < feedData.length; i++) {
          var newsItemDiv = $('<div></div>');
          $("#jogl-news").append(newsItemDiv);
          if (i != 0) {
            newsItemDiv.append('<hr>'); // separator for multiple items
          };
          joglNewsItemContent(newsItemDiv, feedData[i]); // add additional content to news item
          if (!infoTopNews && feedData[i].from.object_type == "project") {
            infoTopNews = true;
            $("#info-jogl-news").append("<hr><h2>Latest News</h2>");
            newsItemDiv.clone().appendTo( "#info-jogl-news" ); // copy first item to info div
          }
        };
      };
    });

    // Load needs.
    const joglNeedsURL = 'https://jogl-backend.herokuapp.com/api/projects/' + joglId + '/needs';
    $.getJSON(joglNeedsURL, function (needsData) {

      // Sort needs and split into "active" and "completed".
      needsData.sort(function (N1, N2) { return sortNeeds(N1, N2); });
      var activeNeeds = needsData.filter(function (N) { return N.status == "active"; });
      var completedNeeds = needsData.filter(function (N) { return N.status == "completed"; });

      if (activeNeeds.length == 0 && completedNeeds.length == 0) {
        $("#jogl-needs").append("<p>No needs currently listed for this project.</p>");
      }

      // Active needs.
      if (activeNeeds.length > 0) {
        $("#jogl-needs").append('<h2>Active Needs</h2>');
        for (var i = 0; i < activeNeeds.length; i++) {
          var needsItemDiv = $('<div></div>');
          $("#jogl-needs").append(needsItemDiv);
          if (i !== 0) {
            needsItemDiv.append('<hr>');
          } else {
            $("#info-jogl-needs").append("<hr><h2>Active needs</h2>");
          }
          joglActiveNeedContent(needsItemDiv, activeNeeds[i]);
          if (i < 3) {
            needsItemDiv.clone().appendTo("#info-jogl-needs");
          }
        };
      };

      // Completed needs.
      if (completedNeeds.length > 0) {
        $("#jogl-needs").append('<h2 class="mt-4">Completed Needs</h2>');
        for (var i = 0; i < completedNeeds.length; i++) {
          var needsItemDiv = $('<div></div>');
          $("#jogl-needs").append(needsItemDiv);
          if (i !== 0) {
            needsItemDiv.append('<hr>');
          }
          joglCompletedNeedContent(needsItemDiv, completedNeeds[i]);
        };
      };
    });
  });
}

// Run this during page load to immediately load the target panel.
$(function () {
  var default_panel = "#activity-panel-info";

  // If not default panel, add hash to URL when a user clicks on a nav item.
  $('#activity-panel-nav .nav-item').not('disabled').on('click', function (e) {
    if (e.target.hash !== default_panel) {
      history.pushState({}, '', e.target.hash);
    } else {
      history.pushState({}, '', window.location.pathname);
    }
  });

  // Run this to handle an existing hash on page load.
  hashHandler();
});

$(document).ready(function () {
  // Add JOGL data after page load, if JOGL URL is defined.
  if (typeof joglURL !== 'undefined') {
    var joglId = /([0-9]+)/g.exec(joglURL)[1];
    addJogl(joglId);
  };
})
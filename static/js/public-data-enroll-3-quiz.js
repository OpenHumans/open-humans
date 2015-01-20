/*global $:true*/

'use strict';

var markdown = require('markdown/lib').markdown;
var yaml = require('js-yaml');
var _ = require('lodash');

// Helper function to parse snippets of Markdown text without wrapping them in
// <p> tags
function markdownSnippet(text) {
  var tree = markdown.parse(text);

  tree.forEach(function (jsonMl) {
    if (jsonMl[0] === 'para') {
      jsonMl.splice(0, 1);
    }
  });

  tree = _.flatten(tree, true);

  return markdown.renderJsonML(markdown.toHTMLTree(tree));
}

function questionPassed(question) {
  return $('#' + question.name + ' input:checked')
    .data('key') === question.correctAnswer;
}

function Form(container) {
  this.$container = $(container);
  this.$formAccordion = $('#form-accordion');
}

function addQuestionsToHTML(form) {
  var templateQuestion = _.template($('#question-template').html());
  form.questions.forEach(function(question) {
    form.$formAccordion.append(templateQuestion(question));
  });

  $('input').click(function () {
    var questionName = $(this).attr('name');

    // Get the question metadata
    var question = _.find(form.questions, {name: questionName});

    // Get the question's containing div
    var $question = $('#' + questionName);

    // Apply classes based on the answer being correct or incorrect
    if (questionPassed(question)) {
      $question.addClass('correct-question');
      $question.removeClass('incorrect-question');
    } else {
      $question.addClass('incorrect-question');
      $question.removeClass('correct-question');
    }

    form.validate();
  });
}

Form.prototype.setup = function () {
  var templateAnswer = _.template($('#answer-template').html());

  var self = this;

  console.log('going to fetch yaml')
  $.get('public_data/config/questions.yaml', function (questionsYaml) {
    console.log('in yaml reading');
    self.questions = yaml.safeLoad(questionsYaml).map(function (question) {
      // Pre-parse sections that can contain Markdown
      question.description = markdown.toHTML(question.description);
      question.explanationText = markdown.toHTML(question.explanationText);
      return question;
    });

    for (var i = 0; i < self.questions.length; i++) {
      var question = self.questions[i];
      question.isExpanded = 'false';
      question.collapsedClass = 'collapsed';
      question.inClass = '';
      if (i === 0) {
        question.isExpanded = 'true';
        question.collapsedClass = '';
        question.inClass = 'in';
      }

      // Parse and add answers to question
      var answers = _(question.answers).map(function (answer, key) {
        // This lets us use unquoted values for 'True' and 'False' in
        // config/questions.yaml
        if (answer === true) {
          answer = 'True';
        } else if (answer === false) {
          answer = 'False';
        }
        return templateAnswer({
          name: question.name,
          key: key,
          answer: markdownSnippet(answer)
        });
      }).join('\n');
      question.answers = answers;
    }

    addQuestionsToHTML(self);
  });
};

Form.prototype.validate = function () {
  // Only validate the form if all questions have been answered
  if ($('input:checked').length !== this.questions.length) {
    return;
  }

  this.$container.addClass('complete');

  if (_.all(this.questions, questionPassed)) {

    if (this.$container.hasClass('failed')) {
      // User has been correcting answers. Draw attention back to the bottom of
      // the page by collapsing all questions.

      // This works in the console for me, but not here:
      // $('.panel-title a').not('.collapsed').click();

      // The following works, but is uglier (visually, not just code).
      $(this.$container).find('.question-panel').each(function () {
        if ($(this).find('.panel-title a').not('collapsed').length) {
          $(this).find('.panel-collapse, .collapse, .in').first().removeClass('in');
          $(this).find('.panel-title a').first().attr('aria-expanded', 'false');
          $(this).find('.panel-title a').first().addClass('collapsed');
        }
      });
    }

    this.$container.addClass('passed');
    this.$container.removeClass('failed');

    $('#submit').removeAttr('disabled');

  } else {
    this.$container.addClass('failed');
    this.$container.removeClass('passed');
  }
};

$(function () {
  var form = new Form('#form-container');
  form.setup();
});

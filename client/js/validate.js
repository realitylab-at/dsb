'use strict';

var _ = require('lodash');
var $ = require('jquery');
var sprintf = require('./utils').sprintf;

function validateForm(formOrElements, param) {
  var elements = formOrElements.is('form') ?
      formOrElements.get(0).elements : formOrElements;

  // Transform to a generic JavaScript array if there is a jQuery one
  elements.get && (elements = elements.get());

  var errors = [];

  _.each(elements, function(item, index) {
    // Get potential errors from the file input
    if ($(item).is('input[type=file]')) {
      var imageErrors = $(item).data('errors');
      if (imageErrors) {
        errors = errors.concat(imageErrors);
      }
    }

    var id = $(item).attr('id');
    var title = $(item).parents('.form-group').find('label').html();

    if (!item.checkValidity()) {
      errors.push({
        refId: id,
        text: sprintf('Bitte füllen Sie das Feld »%s« aus.', title)
      });
    }

    var picker;

    if (picker = $(item).parents('.input-group').data('DateTimePicker')) {
      if (!picker.date()) {
        errors.push({
          refId: id,
          text: sprintf('Bitte füllen Sie das Feld »%s« im korrekten Format aus.', title)
        })
      }
    }
  });

  $(document).trigger('status', {
    type: 'danger',
    content: errors
  });

  return errors.length < 1;
};

module.exports = validateForm;

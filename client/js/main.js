'use strict';

require('./app');

/**
 * TODO:
 * - Develop mobile view for booking matrix
 * - Add confirmation to delete button (e.g. additional click necessary)
 */

/*
// Currently unused code snippets for the record; might be useful again.

// Support of tabbed modals
$(document).on('click', '.modal-footer button:last', function(event) {
  event.preventDefault();
  var self = this;
  var date, param;
  var modal = $('.modal');
  var action = modal.attr('id');
  var nextTab = modal.find('li.active').next();
  if (nextTab.length > 0) {
    nextTab.find('a').tab('show');
  } else {
    $(self).attr('disabled', true);
    switch (action) {
      case 'update-bookings':
      param = {
        building_id: settings.buildingId,
        bookings: $('#update-bookings').data('bookings')
      };
      if (validate(action, param)) {
        doRPC('update_bookings', param).done(function(result) {
          alertSuccess('Ihre Reservierung wurde übernommen.');
          wait(1000).then(function() {
            modal.modal('hide');
          });
        });
      }
      break;
    }
  }
});

// Support of mouse hold for forth and back buttons in bookings modal
var mouseHoldLoop;
$(document).on('mousedown', '.booking-date .btn', function(event) {
  event.preventDefault();
  var self = this;
  var dir = $(self).hasClass('back') ? -1 : 1;
  mouseHoldLoop = setInterval(function() {
    if (!$(self).attr('disabled')) {
      renderBookingMatrix(dir);
    }
  }, 350);
}).on('mouseup mouseleave', '.booking-date .btn', function(event) {
  event.preventDefault();
  clearInterval(mouseHoldLoop);
  mouseHoldLoop = null;
});
*/

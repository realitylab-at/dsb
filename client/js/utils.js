'use strict';

var $ = require('jquery');
var sprintf = require('sprintf').sprintf;

function wait(duration) {
  var deferred = new $.Deferred();
  setTimeout(function() {
    return deferred.resolve();
  }, duration);
  return deferred.promise();
}

function stripTags(str) {
  return str ? $('<div>').html(str).text() : str;
}

function isLayout(size) {
  return $('#layout-tester-' + size).is(':visible');
}

function isTouchScreen() {
  // Touch Screens register with a 64 character hash key; add 1 for the pound sign.
  return location.hash.length === 65;
}

module.exports = {
  isLayout: isLayout,
  isTouchScreen: isTouchScreen,
  sprintf: sprintf,
  stripTags: stripTags,
  wait: wait
};

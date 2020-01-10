'use strict';

var $ = require('jquery');
require('jquery-jsonrpc');

var rpc = function(name, param) {
  var deferred = new $.Deferred();
  $.jsonRPC.withOptions({
    endPoint: settings.apiEndPoint
  }, function() {
    var self = this;
    this.request(name, {
      params: param || {},
      success: function(result) {
        return deferred.resolve.apply(self, arguments);
      },
      error: function(result) {
        var status = {type: 'danger'};
        if (result.error.code === 200) {
          // Backend provides an array like [[null, 'Message Text']]
          status.content = result.error.data[0][1];
        } else if (result.error.code === 401) {
          status.content = 'Leider ist die Anmeldung fehlgeschlagen. Bitte versuchen Sie es erneut.';
        } else {
          status.content = result.error.message;
        }
        status.foo = 'bar';
        $(document).trigger('status', status);
        return deferred.reject.apply(self, arguments);
      }
    });
  });
  return deferred.promise();
};

module.exports = rpc;

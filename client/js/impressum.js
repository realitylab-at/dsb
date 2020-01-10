'use strict';

var React = require('react');
var rpc = require('./rpc');

var Impressum = React.createClass({
  getInitialState: function() {
    return {content: null};
  },

  render: function() {
    return <div dangerouslySetInnerHTML={{__html:this.state.content}} />;
  },

  componentDidMount: function() {
    var self = this;
    rpc('get_impressum', {
      building_id: settings.buildingId
    }).done(function(data) {
      self.setState({content: data.result});
    });
  }
});

module.exports = Impressum;

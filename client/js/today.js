'use strict';

var $ = require('jquery');
var moment = require('moment');
var React = require('react');

var Today = React.createClass({
  getDefaultProps: function() {
    return {updateInterval: 10000};
  },

  getInitialState: function() {
    return {date: 0};
  },

  componentWillMount: function() {
    setInterval(this.update, this.props.updateInterval);
  },

  componentDidMount: function() {
    this.update();
  },

  render: function() {
    var date = moment(this.state.date).format('dddd, LL');
    return <time>{date}</time>;
  },

  update: function() {
    this.setState({date: new Date()});
    var date = moment(this.state.date).format('YYYY-MM-DD');
    $(this.getDOMNode()).attr('datetime', date);
  }
});

module.exports = Today;

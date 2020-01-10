'use strict';

var _ = require('lodash');
var React = require('react');

var Ads = React.createClass({
  render: function() {
    var ads = this.props.data.map(function(url) {
      return (
        <img key={url} className='ad img-responsive' src={url}/>
      );
    });

    return (
      <aside className='col-xs-12 col-sm-2'>
        <h2>
          <small>Werbung</small>
        </h2>
        <div className='content'>
          {ads}
        </div>
      </aside>
    );
  },

  shouldComponentUpdate: function(nextProps, nextState) {
    return _.isEqual(this.props.data, nextProps.data) === false;
  }
});

module.exports = Ads;

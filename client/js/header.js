'use strict';

var React = require('react');
var Today = require('./today');

var Header = React.createClass({
  render: function() {
    var logo;

    if (settings.logo) logo = (
      <span className='pull-left'>
        <img className='img-responsive logo' src={'img/' + settings.logo}/>
      </span>
    );

    return (
      <header>
        <p className='col-md-12'>
          {logo}
          <span className='title'>
            {settings.title}
          </span>
          <span className='brand'>
            <span className='slash'>/</span>Screen
          </span>
          <span className='hidden-xs'>
            <Today updateInterval={1000 * 60 / 60} />
          </span>
        </p>
        <p className='col-md-12 visible-xs'>
          <Today updateInterval={1000 * 60 / 60} />
        </p>
      </header>
    );
  }
});

module.exports = Header;

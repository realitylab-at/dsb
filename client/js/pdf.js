'use strict';

var $ = require('jquery');
var React = require('react');
var utils = require('./utils');

var Link = React.createClass({
  getDefaultProps: function() {
    return {
      icon: 'file',
      text: 'Link zum PDF'
    };
  },

  render: function() {
    var text = this.props.children || this.props.text;
    return (
      <div className='pdf-link'>
        <a className='pdf-view' href={this.props.url} onClick={this.handlePdfClick}>
          <i className={'glyphicon glyphicon-' + this.props.icon}/> {text}
        </a>
      </div>
    );
  },

  handlePdfClick: function(event) {
    if (utils.isTouchScreen()) {
      event.preventDefault();
      $(document).trigger('modal', {
        content: (
          <iframe src={this.props.url + '#toolbar=0&navpanes=0'} width='100%' height='600' seamless></iframe>
        ),
        display: true,
        footer: (
          <div>
            <a className='btn btn-default' data-dismiss='modal' aria-hidden='true'>Schließen</a>
          </div>
        ),
        size: 'lg',
        title: 'Dokument anzeigen'
      });
    }
  }
});

module.exports = {
  Link: Link
};

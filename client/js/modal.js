'use strict';

var _ = require('lodash');
var $ = require('jquery');
var moment = require('moment');
var React = require('react');
var utils = require('./utils');

var Control = React.createClass({
  getDefaultProps: function() {
    return {
      button: true,
      link: true,
      size: 'md'
    };
  },

  componentDidMount: function() {
    var container = $(this.getDOMNode());
    if (this.props['needs-auth']) {
      $('body').hasClass('authenticated') || container.children().attr('disabled', true);
      $(document).on('session', function(event, session) {
        container.children().attr('disabled', !session);
      });
    }
  },

  render: function() {
    var button = this.props.button && (
      <a href='javascript:' {...this.props} onClick={this.handleClick} className='btn btn-default modal-btn'>
        {this.props.children}
      </a>
    );
    var link = this.props.link && (
      <a href='javascript:' {...this.props} onClick={this.handleClick}>
        {this.props.title}
      </a>
    );
    var custom = !this.props.button && !this.props.link && (
      <a href='javascript:' {...this.props} onClick={this.handleClick}>
        {this.props.children}
      </a>
    );
    return (
      <span className={this.props['needs-auth'] && 'needs-auth'}>
        {button} {link} {custom}
      </span>
    );
  },

  handleClick: function(event) {
    event.stopPropagation();

    var container = $(this.getDOMNode());

    if (container.children().attr('disabled')) {
      return $(document).trigger('needs-auth');
    }

    $(document).trigger('modal', {
      content: this.props.content,
      display: true,
      size: this.props.size,
      title: this.props.title
    });
  }
});

var Status = React.createClass({
  getInitialState: function() {
    return {
      type: null,
      content: null
    };
  },

  render: function() {
    return (
      <div className={this.state.content && ('alert alert-' + this.state.type)}
          dangerouslySetInnerHTML={{__html: this.state.content}} />
    );
  }
});

var Modal = React.createClass({
  getInitialState: function() {
    return {
      content: null,
      display: false,
      footer: null,
      size: 'md',
      title: null
    };
  },

  render: function() {
    return (
      <div className='modal fade' tabIndex='-1' role='dialog' aria-labelledby='modal-label' aria-hidden='true'>
        <div className={'modal-dialog modal-' + this.state.size}>
          <form className='modal-content' role='form'>
            <div className='modal-header'>
              <button type='button' className='close' data-dismiss='modal' aria-hidden='true'>&times;</button>
              <h1 className='modal-title'>{this.state.title}</h1>
            </div>
            <div className='modal-body'>
              <Status ref='status'/>
              {this.state.content}
            </div>
            <div className='modal-footer'>
              {this.state.footer || <a className='btn btn-default' data-dismiss='modal' aria-hidden='true'>Schließen</a>}
            </div>
          </form>
        </div>
      </div>
    );
  },

  componentDidMount: function() {
    var self = this;
    var container = $(this.getDOMNode());

    container.modal({
      show: false,
      keyboard: true,
      backdrop: 'static'
    });

    $(document).on('session', function(event, session) {
      session || $(document).trigger('modal', {display: false});
    });

    $(document).on('status', function(event, data) {
      if (!data) {
        container.find('.has-error').removeClass('has-error');
        data = {type: null, content: null};
      } else if (_.isArray(data.content)) {
        if (data.type === 'danger') {
          _.each(data.content, function(error) {
            container.find('#' + error.refId).parents('.form-group').addClass('has-error');
          });
        }
        data.content = _.map(data.content, function(content) {
          return '<div>' + content.text + '</div>';
        }).join('');
      }
      self.refs.status.setState(data);
    });

    $(document).on('modal', function(event, data) {
      if (_.isBoolean(data.display) && data.display === container.is(':hidden')) {
        container.modal(data.display ? 'show' : 'hide');
      }
      self.setState(data);
    });

    container.on('show.bs.modal', function() {
      if (!utils.isLayout('xs')) {
        container.find('.modal-body').css('max-height', $(window).height() * 0.7);
      }
    });

    container.on('hidden.bs.modal', function() {
      self.replaceState({});
      self.refs.status.replaceState({});
    });
  }
});

module.exports = {
  Modal: Modal,
  Control: Control
};

'use strict';

var _ = require('lodash');
var $ = require('jquery');
var React = require('react');
var rpc = require('./rpc');
var validate = require('./validate');
var wait = require('./utils').wait;

var Form = React.createClass({
  render: function() {
    var required = 'required';
    var type, activityRSVP;

    return (
      <div>
        <input id='input-type' type='hidden' value={this.props.type} />
        <input id='input-id' type='hidden' value={this.props.id} />
        {this.props.before}
        <div className='form-group title'>
          <label className='control-label' htmlFor='input-title'>Betreff</label>
          <div className='controls'>
            <input id='input-title' className='form-control' type='text' defaultValue={this.props.subject} required={required} />
          </div>
        </div>
        <div className='form-group'>
          <label className='control-label' htmlFor='input-text'>Text</label>
          <div className='controls'>
            <textarea id='input-text' className='form-control' rows='5' required={required}></textarea>
          </div>
        </div>
        {this.props.after}
      </div>
    );
  },

  componentDidMount: function() {
    $(document).trigger('modal', {
      footer: (
        <div>
          <a href='javascript:' className='btn btn-link' data-dismiss='modal' aria-hidden='true'>
            Abbrechen
          </a> <button onClick={this.handleSubmit} className='btn btn-default'>
            Absenden
          </button>
        </div>
      )
    });
  },

  handleSubmit: function(event) {
    event.preventDefault();
    var container = $(this.getDOMNode());

    var param = {
      building_id: settings.buildingId,
      type: $('#input-type').val(),
      id: parseInt($('#input-id').val(), 10) || null,
      title: $('#input-title').val(),
      text: $('#input-text').val(),
      rsvp: $('#input-rsvp .active input').val()
    };

    if (!validate(container.find(':input', param))) {
      return;
    }

    var target = $(event.target).attr('disabled', true);

    rpc('send_message', param).done(function(data) {
      $(document).trigger('status', {
        type: 'success',
        content: 'Die Nachricht wurde gesendet.'
      });
      wait(1000).then(function() {
        $(document).trigger('modal', {display: false});
      });
    }).fail(function() {
      target.attr('disabled', false);
    });
  }
});

module.exports = {
  Form: Form
};

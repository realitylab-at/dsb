'use strict';

var _ = require('lodash');
var $ = require('jquery');
var MessageForm = require('./message').Form;
var ModalControl = require('./modal').Control;
var moment = require('moment');
var React = require('react');
var rpc = require('./rpc');
var stripTags = require('./utils').stripTags;
var Upload = require('./upload');
var validate = require('./validate');
var wait = require('./utils').wait;

require('moment/locale/de-at.js');

var Form = React.createClass({
  getInitialState: function() {
    return {
      date: parseInt(this.props.date, 10) || new Date(),
      id: this.props.id,
      location: this.props.location,
      text: this.props.text,
      title: this.props.title,
      type: 'activity'
    };
  },

  render: function() {
    return (
      <div>
        <input type='hidden' id='input-id' value={this.state.id} />
        <div className='form-group title'>
          <label className='control-label' htmlFor='input-title'>Überschrift</label>
          <div className='controls'>
            <input id='input-title' className='form-control' type='text' value={this.state.title} onChange={this.handleTitleChange} required />
          </div>
        </div>
        <div className='form-group'>
          <label className='control-label' htmlFor='input-text'>Text</label>
          <div className='controls'>
            <textarea id='input-text' className='form-control' rows='5' required onChange={this.handleTextChange} defaultValue={this.state.text} />
          </div>
        </div>
        <div className='form-group'>
          <label className='control-label' htmlFor='input-date'>Datum</label>
          <div className='input-group col-md-5 controls' ref='date' data-date-format='LL'>
            <input id='input-date' className='form-control' type='text' required />
            <span className='input-group-addon'>
              <i className='glyphicon glyphicon-calendar'></i>
            </span>
          </div>
        </div>
        <div className='form-group'>
          <label className='control-label' htmlFor='input-time'>Uhrzeit</label>
          <div className='input-group col-md-5 controls' ref='time'>
            <input id='input-time' className='form-control' type='text' required />
            <span className='input-group-addon'>
              <i className='glyphicon glyphicon-time'></i>
            </span>
          </div>
        </div>
        <div className='form-group'>
          <label className='control-label' htmlFor='input-location'>Ort</label>
          <div className='controls'>
            <input id='input-location' className='form-control' type='text' value={this.state.location} onChange={this.handleLocationChange} required />
          </div>
        </div>
        <Upload ref='image' />
      </div>
    );
  },

  componentDidMount: function() {
    var deleteButton = (
      <div className='pull-left'>
        <a className='btn btn-danger delete' onClick={this.handleDelete}>
          <i className='glyphicon glyphicon-trash'></i> <span className='hidden-xs'>Löschen</span>
        </a>
      </div>
    );

    $(this.refs.date.getDOMNode()).datetimepicker({
      locale: 'de-at',
      format: 'LL',
      useCurrent: true,
      useStrict: true,
      minDate: moment(this.state.date)
    }).data('DateTimePicker')
        .date(moment(this.state.date));

    $(this.refs.time.getDOMNode()).datetimepicker({
      locale: 'de-at',
      format: 'LT',
      stepping: 15,
      useCurrent: true,
      useStrict: true
    }).data('DateTimePicker')
        .date(moment(this.state.date));

    $(document).trigger('modal', {
      footer: (
        <div>
          {this.props.id && deleteButton}
          <a className='btn btn-link' data-dismiss='modal' aria-hidden='true'>
            Abbrechen
          </a>
          <button onClick={this.handleSubmit} className='btn btn-default'>
            Speichern
          </button>
        </div>
      )
    });
  },

  handleLocationChange: function(event) {
    this.setState({location: event.target.value});
  },

  handleTextChange: function(event) {
    this.setState({text: event.target.value});
  },

  handleTitleChange: function(event) {
    this.setState({title: event.target.value});
  },

  handleSubmit: function(event) {
    event.preventDefault();

    var container = $(this.getDOMNode());

    if (!validate(container.find(':input', param))) {
      return;
    }

    var date = $(this.refs.date.getDOMNode()).data('DateTimePicker').date();
    var time = $(this.refs.time.getDOMNode()).data('DateTimePicker').date();

    date.set('hours', time.get('hours'));
    date.set('minutes', time.get('minutes'));

    this.setState({date: +date});

    var param = _.clone(this.state);
    param.building_id = settings.buildingId;
    param.date = +date; // this.state.date is not updated, yet!

    if (this.refs.image && this.refs.image.state.files.length > 0) {
      param.image = this.refs.image.state.files[0];
    }

    var target = $(event.target).attr('disabled', true);

    rpc('add_content', param).done(function(data) {
      $(document).trigger('status', {
        type: 'success',
        content: 'Ihr Beitrag wurde hinzugefügt.'
      });
      wait(1000).then(function() {
        $(document).trigger('modal', {display: false});
        $(document).trigger('posting', {
          action: param.id ? 'update' : 'add',
          posting: data.result
        });
      });
    }).fail(function() {
      target.attr('disabled', false);
    });
  },

  handleDelete: function(event) {
    event.preventDefault();

    var target = $(event.target).attr('disabled', true);

    rpc('delete_content', {id: this.state.id}).done(function(data) {
      if (data.result) {
        $(document).trigger('status', {
          type: 'success',
          content: 'Der Beitrag wurde gelöscht.'
        });
        wait(1000).then(function() {
          $(document).trigger('modal', {display: false});
          $(document).trigger('posting', {
            action: 'delete',
            posting: data.result
          });
        });
      } else {
        $(document).trigger('status', {
          type: 'danger',
          content: 'Sie haben nicht die Berechtigung, diesen Beitrag zu löschen.'
        });
      }
    }).fail(function() {
      target.attr('disabled', false);
    });
  }
});

var Posting = React.createClass({
  getInitialState: function() {
    return this.props;
  },

  render: function() {
    var content = this.state.content;

    var rsvpClasses = {};
    _.each(['unknown', 'yes', 'maybe', 'no'], function(choice) {
      rsvpClasses[choice] = 'btn btn-default' +
          (content.rsvp.selected === choice ? ' active' : '');
    });

    if (!content.rsvp.selected) {
      rsvpClasses.unknown += ' active';
    }

    var rsvpButtons = (
      <div className='form-group'>
        <label className='control-label' htmlFor='input-rsvp'>Teilnahme</label>
        <div className='controls'>
          <div id='input-rsvp' className='btn-group' data-toggle='buttons'>
            <label className={rsvpClasses.unknown}>
              <input type='radio' name='rsvp' value='unknown'/> Weiß noch nicht
            </label>
            <label className={rsvpClasses.yes}>
              <input type='radio' name='rsvp' value='yes'/> Ja
            </label>
            <label className={rsvpClasses.maybe}>
              <input type='radio' name='rsvp' value='maybe'/> Vielleicht
            </label>
            <label className={rsvpClasses.no}>
              <input type='radio' name='rsvp' value='no'/> Nein
            </label>
          </div>
        </div>
      </div>
    );

    var messageForm = <MessageForm id={content.id}
        before={rsvpButtons}
        type={content.type}
        subject={'Re: ' + content.title} />;

    var editForm = <Form id={content.id}
        date={content.date}
        location={content.location}
        type={content.type}
        title={content.title}
        text={content.text} />;

    return (
      <article className={content.type}>
        <h4 onClick={this.handleClick}>
          {stripTags(content.title)}
        </h4>
        <div className='body hidden-xs'>
          <p>{content.image}</p>
          <div className='text' dangerouslySetInnerHTML={{__html: content.html}}/>
          <p>
            <div className='small text-muted'>Wann und wo?</div>
            {moment(parseInt(content.date, 10)).format('LLLL')} Uhr, {content.location}.
            <div className='rsvp small'>
              <span className='label label-success'>{content.rsvp.yes > 0 ? content.rsvp.yes + ' Ja' : ''}</span> <span className='label label-info'>{content.rsvp.maybe > 0 ? content.rsvp.maybe + ' Vielleicht' : ''}</span>
            </div>
          </p>
          <div className='controls'>
            <p className='small text-muted'>
              <i className='glyphicon glyphicon-user'/> {content.creator.group} {moment(content.created).fromNow()}
            </p>
            <ModalControl title='Antworten' content={messageForm} link={false} ref='sendButton' needs-auth={true}>
              <i className='glyphicon glyphicon-envelope'></i> Antworten
            </ModalControl> <ModalControl title='Bearbeiten' content={editForm} link={false} ref='editButton'>
              <i className='glyphicon glyphicon-pencil'/>
            </ModalControl>
         </div>
        </div>
        <div className='clearfix'/>
        <hr/>
      </article>
    );
  },

  componentDidMount: function() {
    var self = this;
    var editButton = $(self.refs.editButton.getDOMNode());

    $('body').hasClass('authenticated') || editButton.hide();

    $(document).on('session', function(event, session) {
      if (session && session.id === self.state.content.creator.id) {
        editButton.show();
      } else {
        editButton.hide();
      }
    });
  },

  componentWillReceiveProps: function(props) {
    this.setState(props);
  },

  handleClick: function(event) {
    event.preventDefault();
    $(event.currentTarget).next('.body')
        .toggleClass('hidden-xs', 'not-hidden-xs');
  }
});

module.exports = {
  Form: Form,
  Posting: Posting
};


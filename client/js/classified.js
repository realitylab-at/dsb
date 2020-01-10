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

var Form = React.createClass({
  getInitialState: function() {
    return {
      id: this.props.id,
      text: this.props.text,
      title: this.props.title,
      type: this.props.type || 'request'
    };
  },

  render: function() {
    var requestClass = 'btn btn-default ' + (this.state.type === 'request' && 'active');
    var offerClass = 'btn btn-default ' + (this.state.type === 'offer' && 'active');

    return (
      <div>
        <input type='hidden' id='input-id' value={this.state.id} />
        <div className='form-group'>
          <label className='control-label'>Art</label>
          <div className='controls'>
            <div id='input-type' className='btn-group' data-toggle='buttons'>
              <label className={requestClass} onClick={this.handleTypeChange}>
                <input type='radio' name='type' value='request'/> Suche
              </label>
              <label className={offerClass} onClick={this.handleTypeChange}>
                <input type='radio' name='type' value='offer'/> Biete
              </label>
            </div>
          </div>
        </div>
        <div className='form-group title'>
          <label className='control-label' htmlFor='input-title'>
            {this.state.type === 'request' ? 'Suche' : 'Biete'}
          </label>
          <div className='controls'>
            <input id='input-title' className='form-control' type='text' value={this.state.title} onChange={this.handleTitleChange} required />
          </div>
        </div>
        <div className='form-group'>
          <label className='control-label' htmlFor='input-text'>Beschreibung</label>
          <div className='controls'>
            <textarea id='input-text' className='form-control' rows='5' onChange={this.handleTextChange} required defaultValue={this.state.text} />
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

    $(document).trigger('modal', {
      footer: (
        <div>
          {this.props.id && deleteButton}
          <a className='btn btn-link' data-dismiss='modal' aria-hidden='true'>Abbrechen</a>
          <button onClick={this.handleSubmit} className='btn btn-default' type='submit'>
            Speichern
          </button>
        </div>
      )
    });
  },

  handleTextChange: function(event) {
    this.setState({text: event.target.value});
  },

  handleTitleChange: function(event) {
    this.setState({title: event.target.value});
  },

  handleTypeChange: function(event) {
    this.setState({type: $(event.currentTarget).find('input').val()});
  },

  handleSubmit: function(event) {
    event.preventDefault();

    var self = this;
    var container = $(this.getDOMNode());

    var param = _.clone(this.state);
    param.building_id = settings.buildingId;

    if (this.refs.image && this.refs.image.state.files.length > 0) {
      param.image = this.refs.image.state.files[0];
    }
    if (!validate(container.find(':input', param))) {
      return;
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

    var self = this;
    var target = $(event.target).attr('disabled', true);

    rpc('delete_content', {id: this.state.id}).done(function(data) {
      if (data.result) {
        $(document).trigger('status', {
          type: 'success',
          content: 'Der Eintrag wurde gelöscht.'
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
          content: 'Sie haben nicht die Berechtigung, diesen Eintrag zu löschen.'
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

    var messageForm = <MessageForm id={content.id}
        type={content.type}
        subject={'Re: ' + content.title} />;

    var editForm = <Form id={content.id}
        type={content.type}
        title={content.title}
        text={content.text} />;

    return (
      <article className={content.type}>
        <h4 onClick={this.handleClick}>
          {content.type === 'request' ? 'Suche' : 'Biete'}: {stripTags(content.title)}
        </h4>
        <div className='body hidden-xs'>
          <p>{content.image}</p>
          <div className='text' dangerouslySetInnerHTML={{__html: content.html}} />
          <div className='controls'>
            <p className='small text-muted'>
              <i className='glyphicon glyphicon-user'></i> {content.creator.group} {moment(content.created).fromNow()}
            </p>
            <ModalControl title='Nachricht senden' content={messageForm} link={false} ref='sendButton'needs-auth={true}>
              <i className='glyphicon glyphicon-envelope'></i> Antworten
            </ModalControl> <ModalControl title='Bearbeiten' content={editForm} link={false} ref='editButton'>
              <i className='glyphicon glyphicon-pencil'></i>
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
    var editButton = $(self.refs.editButton.getDOMNode())

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

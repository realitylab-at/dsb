'use strict';

var _ = require('lodash');
var $ = require('jquery');
var ModalControl = require('./modal').Control;
var moment = require('moment');
var React = require('react');
var rpc = require('./rpc');
var utils = require('./utils');
var validate = require('./validate');
var wait = require('./utils').wait;

var Session = React.createClass({
  statics: {
    signOut: function() {
      rpc('sign_out').then(function() {
        $('body').removeClass('authenticated');
        $(document).trigger('session', null);
      });
    }
  },

  getInitialState: function() {
    return {session: null};
  },

  render: function() {
    var username, displaySignIn, displaySignOut;
    if (this.state.session) {
      username = this.state.session.username;
      displaySignIn = 'hidden';
    } else {
      displaySignOut = 'hidden';
    }
    return (
      <span>
        <SignInButton className={displaySignIn} />
        <SignOutButton className={displaySignOut} username={username} />
      </span>
    );
  },

  componentDidMount: function() {
    var self = this;
    $(document).on('session', function(event, session) {
      self.setState({session: session});
      $('body')[session ? 'addClass' : 'removeClass']('authenticated');
    });
  },

  shouldComponentUpdate: function(props, state) {
    return !!state.session && !this.state.session ||
      !state.session && !!this.state.session;
  }
});

var SignInButton = React.createClass({
  render: function() {
    return (
      <form className='form-horizontal' {...this.props}>
        <ModalControl title='Anmeldung' link={false} type='submit' content={<SignInForm/>}>
          <i className='glyphicon glyphicon-user'></i> Anmelden
        </ModalControl>
      </form>
    );
  },

  componentDidMount: function() {
    var self = this;
    var container = $(this.getDOMNode());
    $(document).on('needs-auth', function(event) {
      container.popover({
        placement: 'top',
        title: 'Bitte melden Sie sich an.'
      }).popover('show');
      wait(3000).then(function() {
        container.popover('destroy');
      });
    });
  }
});

var SignOutButton = React.createClass({
  render: function() {
    return (
      <form className='form-horizontal' {...this.props}>
        <span>
          {this.props.username}
        </span> <button className='btn btn-default modal-btn' onClick={this.handleClick} type='submit'>
          <i className='glyphicon glyphicon-user'></i> Abmelden
        </button> <SignOutTimer/>
      </form>
    );
  },

  handleClick: function(event) {
    event.preventDefault();
    Session.signOut();
  }
});

var SignOutTimer = React.createClass({
  getDefaultProps: function() {
    return {
      timeout: settings.timeout * 60 * 1000,
      updateInterval: 1000
    };
  },

  getInitialState: function() {
    return {
      timeout: this.props.timeout,
      lastActivity: new Date()
    };
  },

  componentDidMount: function() {
    var self = this;
    var container = $(this.getDOMNode());
    var scheduler = null;

    if (!utils.isTouchScreen()) container.hide();

    $(document).on('session', function(event, session) {
      if (utils.isTouchScreen() && session) {
        self.setState({lastActivity: new Date()});
        scheduler = setInterval(self.update, self.props.updateInterval);
      } else {
        self.setState({timeout: self.props.timeout});
        clearInterval(scheduler);
      }
    });

    $(document).on('click', function() {
      self.setState({lastActivity: new Date()});
    });
  },

  render: function() {
    var time = moment(this.state.timeout).format('mm:ss');
    return <time>{time}</time>;
  },

  update: function() {
    var container = $(this.getDOMNode());
    var now = new Date();
    var delta = this.state.lastActivity - now + this.props.timeout;
    this.setState({timeout: delta});
    if (delta > 1000) {
      $(this.getDOMNode()).attr('time', moment(delta).format('mm:ss'));
    } else {
      Session.signOut();
    }
  }
});

var SignInForm = React.createClass({
  getInitialState: function() {
    return {
      password: null,
      username: null
    }
  },

  render: function() {
    return (
      <div>
        <div className='form-group'>
          <label className='control-label' htmlFor='input-username'>Top-Kennung</label>
          <div className='controls'>
            <input className='form-control' type='text' id='input-username' onChange={this.handleUsernameChange} placeholder='z.B. top456' required />
          </div>
        </div>
        <div className='form-group'>
          <label className='control-label' htmlFor='input-password'>Kennwort</label>
          <div className='controls'>
            <input className='form-control' type='password' id='input-password' onChange={this.handlePasswordChange} placeholder='Ihr persönliches Kennwort' required />
          </div>
        </div>
        <a className='btn-link' href='javascript:' onClick={this.handleReset}>
          Kennwort zurücksetzen.
        </a>
      </div>
    );
  },

  componentDidMount: function() {
    $(document).trigger('modal', {
      footer: (
        <div>
          <a href='javascript:' className='btn btn-link' data-dismiss='modal' aria-hidden='true'>
            Abbrechen
          </a> <button onClick={this.handleSubmit} className='btn btn-default' type='submit' data-submit='Senden'>
            Anmelden
          </button>
        </div>
      )
    });
  },

  handleUsernameChange: function(event) {
    this.setState({username: event.target.value});
  },

  handlePasswordChange: function(event) {
    this.setState({password: event.target.value});
  },

  handleSubmit: function(event) {
    event.preventDefault();
    var container = $(this.getDOMNode());

    var param = {
      building_id: settings.buildingId,
      // Autofill and onChange do not mix very well :/
      username: this.state.username || $('#input-username').val(),
      password: this.state.password || $('#input-password').val()
    };

    if (!validate(container.find(':input', param))) {
      return;
    }

    var target = $(event.target).attr('disabled', true);

    rpc('sign_in', param).done(function(data) {
      if (data.result.reset_date) {
        $(document).trigger('modal', {
          content: <ResetForm username={param.username} password={param.password} />
        });
        target.attr('disabled', false);
        return;
      }

      $(document).trigger('status', {
        type: 'success',
        content: 'Sie haben sich erfolgreich angemeldet.'
      });

      wait(1000).then(function() {
        $(document).trigger('modal', {display: false});
        $(document).trigger('session', data.result);
      });
    }).fail(function() {
      target.attr('disabled', false);
    });
  },

  handleReset: function(event) {
    event.preventDefault();
    var username = $('#input-username').val();
    if (!username) {
      $(document).trigger('status', {
        type: 'danger',
        content: [{
          refId: 'input-username',
          text: 'Bitte füllen Sie das Feld »Top-Kennung« aus.'
        }]
      });
    } else {
      var param = {
        username: username,
        building_id: settings.buildingId
      };
      rpc('password_reset', param).done(function() {
        $(document).trigger('status', {
          type: 'success',
          content: 'Ein vorläufiges Kennwort wird Ihnen per E-Mail zugesendet.'
        });
        wait(1000).then(function() {
          $('.modal').modal('hide');
        });
      });
    }
  }
});

var ResetForm = React.createClass({
  getInitialState: function() {
    return {
      password: null,
      passwordInputType: 'password'
    };
  },

  render: function() {
    return (
      <div className='form-group'>
        <input type='hidden' value={this.props.username} />
        <input type='hidden' value={this.props.password} />
        <label className='control-label' htmlFor='input-new-password'>Neues Kennwort:</label>
        <div className='controls'>
          <div className='input-group'>
            <input id='input-new-password' className='form-control' type={this.state.passwordInputType} placeholder='Ihr selbstgewähltes, persönliches Kennwort' onChange={this.handlePasswordChange} required />
            <span onMouseDown={this.handlePasswordToggle} onMouseUp={this.handlePasswordToggle} className='input-group-addon'>
              <i className='glyphicon glyphicon-eye-open'></i>
            </span>
          </div>
        </div>
      </div>
    );
  },

  componentDidMount: function() {
    $(document).trigger('status', {
      type: 'info',
      content: 'Bitte geben Sie ein neues, von Ihnen definiertes Kennwort ein.'
    });

    $(document).trigger('modal', {
      title: 'Kennwort-Änderung',
      footer: (
        <div>
          <a href='javascript:' className='btn btn-link' data-dismiss='modal' aria-hidden='true'>
            Abbrechen
          </a> <button onClick={this.handleSubmit} className='btn btn-default'>
            Kennwort speichern
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
      username: this.props.username,
      new_password: this.state.password,
      temp_password: this.props.password
    };

    if (!validate(container.find(':input', param))) {
      return;
    }

    rpc('password_reset', param).done(function(data) {
      $(document).trigger('status', {
        type: 'success',
        content: 'Sie haben sich erfolgreich angemeldet.'
      });
      wait(1000).then(function() {
        $(document).trigger('modal', {display: false});
        $(document).trigger('session', data.result.session);
      });
    });
  },

  handlePasswordChange: function(event) {
    this.setState({password: event.target.value});
  },

  handlePasswordToggle: function(event) {
    event.preventDefault();
    var currentType = this.state.passwordInputType;
    this.setState({passwordInputType: currentType === 'password' ? 'text' : 'password'});
  }
});

module.exports = Session;

'use strict';

var Bookings = require('./booking');
var MessageForm = require('./message').Form;
var ModalControl = require('./modal').Control;
var React = require('react');
var Session = require('./session');

var Main = React.createClass({

  render: function() {
    return (
      <div className='btn-group col-xs-12'>
        <ModalControl title='Schaden melden'
            content={<MessageForm type='generic' subject='Schadensmeldung' />}
            link={false}
            needs-auth={true}>
          <i className='glyphicon glyphicon-warning-sign'></i>
        </ModalControl>

        <ModalControl title='Hausverwaltung benachrichtigen'
            content={<MessageForm type='generic' subject='An die Hausverwaltung' />}
            link={false}
            needs-auth={true}>
          <i className='glyphicon glyphicon-envelope'></i>
        </ModalControl>

        <div className='pull-right'>
          <Session/>
        </div>
      </div>
    );
  }
});

module.exports = {
  Main: Main
};

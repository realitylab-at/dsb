'use strict';

var Bookings = require('./booking');
var Impressum = require('./impressum');
var ModalControl = require('./modal').Control;
var MessageForm = require('./message').Form;
var React = require('react');
var Session = require('./session');

var Footer = React.createClass({

  render: function() {
    return (
      <footer>
        <div className='col-xs-10'>
          <menu type='toolbar'>
            <li>
              <ModalControl title='Schaden melden'
                  content={<MessageForm type='generic' subject='Schadensmeldung' />}
                  needs-auth={true}>
                <i className='glyphicon glyphicon-warning-sign'></i>
              </ModalControl>
            </li>
            <li>
              <ModalControl title='Hausverwaltung benachrichtigen'
                  content={<MessageForm type='generic' subject='An die Hausverwaltung' />}
                  needs-auth={true}>
                <i className='glyphicon glyphicon-envelope'></i>
              </ModalControl>
            </li>
            <li>
              <ModalControl title='Reservieren'
                  content={<Bookings/>}
                  needs-auth={true}
                  size='lg'>
                <i className='glyphicon glyphicon-plus'></i>
              </ModalControl>
            </li>
            <li className='user-status'>
              <Session/>
            </li>
          </menu>
        </div>
        <div className='col-xs-2'>
          <menu type='toolbar'>
            <li>
              <ModalControl title='Impressum'
                  content={<Impressum/>}
                  button={false}/>
            </li>
          </menu>
        </div>
      </footer>
    );
  }

});

module.exports = Footer;

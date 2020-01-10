'use strict';

if (parent.frames.length > 0) {
  top.location.href = document.location;
}

var $ = require('jquery');
var _ = require('lodash');

_.defaults(settings, {
  apiEndPoint: '/-/api/',
  errorThreshold: 3,
  scheduler: 30,  // seconds
  timeout: 10     // minutes
});

var FileAPI = {
  staticPath: 'js/file-api/',
  debug: false
};

require('bootstrap');
require('bootstrap-fileupload');
require('bootstrap-datetimepicker');
require('console');
require('fileapi');
require('polyfiller');

webshim.debug = false;
webshim.setOptions({
  basePath: 'js/shims/',
  forms: {addValidators: true}
});
webshim.polyfill('forms');

var ActivityForm = require('./activity').Form;
var ClassifiedForm = require('./classified').Form;
var Ads = require('./ads');
var Footer = require('./footer');
var Header = require('./header');
var Modal = require('./modal').Modal;
var ModalControl = require('./modal').Control;
var PdfLink  = require('./pdf').Link;
var React = require('react');
var rpc = require('./rpc');
var Section = require('./section');
var Session = require('./session');
var utils = require('./utils');

if (!Date.now) {
  Date.now = function() {
    return (new Date()).getTime();
  };
}

var App = React.createClass({
  getDefaultProps: function() {
    var props = {
      boardKey: location.hash.substr(1),
      errorCounter: 0
    };
    return props;
  },

  getInitialState: function() {
    return {
      ads: [],
      emergencyPdf: null,
      lastUpdate: null,
      postings: [],
      session: null,
      sessionLocked: false
    };
  },

  render: function() {
    var sections = {
      activity: [],
      information: [],
      classified: []
    };

    _.each(this.state.postings, function(posting, index) {
      if (posting.type === 'offer' || posting.type === 'request') {
        sections.classified.push(posting);
      } else {
        sections[posting.type].push(posting);
      }
    });

    var activityButton = (
      <ModalControl title='Aktivität starten'
          content={<ActivityForm/>}
          className='auth'
          button={false}
          link={false}
          needs-auth={true}>
        <i className='glyphicon glyphicon-pushpin'/>
      </ModalControl>
    );

    var classifiedButton = (
      <ModalControl title='Anzeige aufgeben'
          content={<ClassifiedForm/>}
          className='auth'
          button={false}
          link={false}
          needs-auth={true}>
        <i className='glyphicon glyphicon-pushpin'/>
      </ModalControl>
    );

    var activityFooter = (
      <ModalControl title='Aktivität starten'
          content={<ActivityForm/>}
          className='auth'
          link={false}
          needs-auth={true}>
        <i className='glyphicon glyphicon-plus'/> Aktivität starten
      </ModalControl>
    );

    var classifiedFooter = (
      <ModalControl title='Anzeige aufgeben'
          content={<ClassifiedForm/>}
          className='auth'
          link={false}
          needs-auth={true}>
        <i className='glyphicon glyphicon-plus'/> Anzeige aufgeben
      </ModalControl>
    );

    var informationFooter = this.state.emergencyPdf && (
      <PdfLink url={this.state.emergencyPdf} icon='exclamation-sign'>
        <b>Notrufnummern</b>
      </PdfLink>
    );

    var Menu = require('./menu').Main;

    return (
      <div className='container-fluid'>
        <div className='row'>
          <Header/>
        </div>
        <div className='menu visible-xs row'>
          <Menu/>
        </div>
        <div className='row'>
          <div className='col-sm-10'>
            <div className='row'>
              <Section key={1} type={'information'}
                  title={'Information'}
                  postings={sections.information}
                  footer={informationFooter}
                  className='col-sm-4' />

              <Section key={2} type={'activity'}
                  title={'Aktivitäten'}
                  button={activityButton}
                  postings={sections.activity}
                  footer={activityFooter} />

              <Section key={3} type={'classified'}
                  title={'Suche/Biete'}
                  button={classifiedButton}
                  postings={sections.classified}
                  footer={classifiedFooter} />
            </div>
          </div>
          <Ads data={this.state.ads} className='col-sm-2' />
        </div>
        <div className='row hidden-xs'>
          <Footer/>
        </div>
        <Modal ref='modal' />
      </div>
    );
  },

  componentWillMount: function() {
    if (utils.isTouchScreen()) {
      document.oncontextmenu = function() {
        return false;
      };
      $('body').css({cursor: 'none'})
          .addClass('touch-screen');
    }
    this.update();
    if (this.props.updateInterval) {
      setInterval(this.update, this.props.updateInterval);
    }
  },

  componentDidMount: function() {
    var self = this;

    $(document).on('posting', function(event, data) {
      switch (data.action) {
        case 'add':
        self.state.postings.unshift(data.posting);
        self.setState({postings: self.state.postings});
        break;

        case 'delete':
        _.remove(self.state.postings, {id: data.posting.id});
        self.setState({postings: self.state.postings});
        break;
      }
    });

    $(document).on('session', function(event, session) {
      self.setState({session: session, sessionLocked: true});
    });
  },

  update: function() {
    var self = this;

    rpc('get_content', {
      building_id: settings.buildingId,
      board_key: this.props.boardKey,
      last_update: self.state.lastUpdate
    }).done(function(data) {
      if (self.props.errorCounter >= settings.errorThreshold) {
        $('.modal').modal('hide');
        self.props.errorCounter = 0;
      }

      self.setState({lastUpdate: Date.now()});

      if (!data.result) return;

      self.setState({
        ads: data.result.ads,
        emergencyPdf: data.result.emergency_pdf,
        postings: data.result.content
      });

      // If the session expired via event the sessionLocked property was set.
      // In this case we once prevent any session update contained in content data.
      // This should fix the issue that after signing in/out the session state is
      // reverted by a session object contained in content data retrieved shortly after.
      // (Welcome to async hell!)
      if (self.state.sessionLocked) {
        self.setState({sessionLocked: false});
        return;
      }

      var session = data.result.session;
      if (session && !self.state.session ||
          session && self.state.session && session.id !== self.state.session.id) {
        $(document).trigger('session', session);
      } else if (!session && self.state.session) {
        Session.signOut();
      }

      self.resizeSections();
      self.resizePortraitImages();

      window.onresize = self.resizeSections;
      document.title = data.result.title;

    }).fail(function() {
      if (self.props.errorCounter >= settings.errorThreshold) {
        self.refs.modal.setState({
          title: 'Störung',
          content: 'An der Behebung wird gearbeitet. Danke für Ihr Verständnis.',
          footer: <span/>
        });
        $(document).trigger('modal', {display: true});
      }

      self.props.errorCounter += 1;
    });
  },

  // FIXME: Dirty hack to resize portrait images
  resizePortraitImages: function () {
    if (utils.isLayout('xs')) {
      return;
    }
    $('article img').each(function() {
      var self = this;
      var img = new Image();
      img.src = this.src;
      img.onload = function() {
        if (this.width - this.height < 0) {
          $(self).css({
            'max-width': '100%',
            'max-height': 'initial'
          });
        }
      };
    });
  },

  // FIXME: Dirty hack to resize the height of the section columns
  resizeSections: function() {
    if (utils.isLayout('xs')) {
      return;
    }
    var content = $('.content').outerHeight(0);
    var documentHeight = $(document).outerHeight();
    var headerHeight = $('.row').first().outerHeight();
    var titleHeight = $('section h2').outerHeight();
    var bottomHeight = $('section .bottom').eq(1).outerHeight();
    var footerHeight = $('footer').height();
    var height = documentHeight - headerHeight - footerHeight - titleHeight - bottomHeight;
    content.outerHeight(height - 30);
  }
});

$(function() {
  React.render(
    <App updateInterval={settings.scheduler * 1000} />,
    document.getElementById('main')
  );
});

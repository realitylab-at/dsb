'use strict';

var _ = require('lodash');
var $ = require('jquery');
var Activity = require('./activity').Posting;
var Classified = require('./classified').Posting;
var ModalControl = require('./modal').Control;
var moment = require('moment');
var PdfLink = require('./pdf').Link;
var React = require('react');
var utils = require('./utils');

var Posting = React.createClass({
  getInitialState: function() {
    return {
      content: this.props.content
    };
  },

  render: function() {
    var content = this.state.content;

    var category, image, controls, button;
    var activityDetails, activityRSVP;
    var text = [];

    var paragraphs = content.text.split(new RegExp('(?:\\r\\n|\\r{2}|\\n{2})', 'g'));
    _.each(paragraphs, function(paragraph, index) {
      /* var text = $.trim(paragraph) || '\xa0'; 'if we want empty lines' */
      paragraph = $.trim(utils.stripTags(paragraph));
      if (paragraph) {
        text.push('<p>');
        var lines = paragraph.split(new RegExp('(?:\\r{1}|\\n{1})', 'g'));
        if (lines.length > 1) {
          _.each(lines, function(line, index) {
            line = $.trim(utils.stripTags(line));
            line && text.push('<div>', line, '</div>');
          });
        } else {
          text.push(paragraph);
        }
        text.push('</p>');
      }
    });

    content.html = text.join('');

    if (content.image.url) {
      var image = (
        <img src={content.image.url} className='img-responsive'/>
      );

      var thumbnail = (
        <div className='image'>
          <img src={content.image.url} className='img-responsive'/>
        </div>
      );

      content.image = utils.isLayout('xs') ? thumbnail : (
        <ModalControl title='Bild vergrößern' content={image} link={false} button={false}>
          {thumbnail}
        </ModalControl>
      );
    }

    switch (content.type) {
      case 'activity':
      return <Activity content={content} />;

      case 'offer':
      case 'request':
      return <Classified content={content} />;
    }

    return (
      <article className={content.type}>
        <h4 onClick={this.handleClick}>
          {utils.stripTags(content.title)}
        </h4>
        <div className='body not-hidden-xs'>
          <div className='text' dangerouslySetInnerHTML={{__html: content.html}}/>
          <div className='controls'>
            <p>{content.pdf && <PdfLink url={content.pdf}/>}</p>
            <p className='small text-muted'>
              <i className='glyphicon glyphicon-user'></i> {content.creator.group} {moment(content.created).fromNow()}
            </p>
         </div>
        </div>
        <div className='clearfix'/>
        <hr/>
      </article>
    );
  },

  componentWillReceiveProps: function(props) {
    this.setState(props);
  },

  componentDidMount: function() {
    var self = this;
    var container = self.getDOMNode();

    $(document).on('posting', function(event, data) {
      if (data.posting.id === self.state.content.id) {
        if (data.action === 'update') {
          self.setState({content: data.posting});
        }
      }
    });
  },

  handleClick: function(event) {
    event.preventDefault();
    $(event.currentTarget).next('.body')
        .toggleClass('hidden-xs', 'not-hidden-xs');
  }
});

module.exports = Posting;

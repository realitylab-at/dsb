'use strict';

var _ = require('lodash');
var $ = require('jquery');
var Posting = require('./posting');
var React = require('react/addons');

var ReactCSSTransitionGroup = React.addons.CSSTransitionGroup;

var Section = React.createClass({
  getInitialState: function() {
    return this.props;
  },

  render: function() {
    var postings = this.state.postings.map(function(posting) {
      return <Posting key={posting.id} content={posting} />;
    });

    return (
      <section className={this.props.className || 'col-sm-4'}>
        <h2 onClick={this.handleClick}>
          {this.props.title}
          <span className='pull-right visible-xs'>
            {this.props.button}
          </span>
        </h2>
        <div className='content' ref='content'>
            {postings}
        </div>
        <div className='bottom hidden-xs'>
          {this.props.footer}
        </div>
      </section>
    );
  },

  componentDidMount: function() {
    var self = this;
    $(document).on('session', function(event, session) {
      session || (self.refs.content.getDOMNode().scrollTop = 0);
    });
  },

  componentWillReceiveProps: function(props) {
    this.setState(props);
  },

  handleClick: function(event) {
    event.preventDefault();
    $(event.currentTarget).next('.content')
        .toggleClass('hidden-xs');
  }
});

module.exports = Section;

'use strict';

var _ = require('lodash');
var $ = require('jquery');
var moment = require('moment');
var rpc = require('./rpc');
var React = require('react');
var wait = require('./utils').wait;

require('moment/locale/de-at.js');

var Matrix = React.createClass({
  getDefaultProps: function() {
    var rowSize = 12;
    return {
      end: rowSize,
      rowSize: rowSize,
      start: 0
    }
  },

  getInitialState: function() {
    return {
      bookables: null,
      dates: null,
      end: this.props.end,
      max_booking_days: 0,
      next: -1,
      prev: -1,
      start: this.props.start,
      timestamp: null,
      unit: 1
    };
  },

  render: function() {
    return (
      <div className='bookings'>
        <div className='input-group col-xs-3 pull-left' ref='date'>
          <input className='form-control' type='text' required />
          <span className='input-group-addon'>
            <i className='glyphicon glyphicon-calendar'/>
          </span>
        </div>
        <div className='btn-group pull-right'>
          <a href='javascript:' ref='backButton' className='btn btn-default back' onClick={this.handleBackClick} disabled='disabled'>
            <i className='glyphicon glyphicon-chevron-left'/>
          </a>
          <a href='javascript:' ref='forthButton' className='btn btn-default forth' onClick={this.handleForthClick}>
            <i className='glyphicon glyphicon-chevron-right'/>
          </a>
        </div>
        <div className='clearfix'></div>
        {this.renderMatrix()}
      </div>
    );
  },

  componentDidMount: function() {
    var self = this;
    var date = $(this.refs.date.getDOMNode());

    this.cache = [];

    this.datePicker = date.datetimepicker({
      locale: 'de-at',
      format: 'ddd LL',
      useCurrent: false,
      minDate: moment(new Date()).startOf('day')
    }).data('DateTimePicker');

    date.on('dp.change', function (event) {
      var minDate = self.datePicker.minDate();
      var offset = event.date ? event.date.startOf('day').diff(minDate, 'days') : 0;
      self.fetch(offset * (self.state.unit === 1 ? 2 : 1));
    });

    this.fetch();

    $(document).trigger('modal', {
      footer: (
        <div>
          <a className='btn btn-link' data-dismiss='modal' aria-hidden='true'>Abbrechen</a>
          <button className='btn btn-default' onClick={this.handleSubmit}>Speichern</button>
        </div>
      )
    });
  },

  componentWillUnmount: function() {
    this.datePicker.destroy();
    this.cache = null;
  },

  fetch: function(offset, type) {
    var self = this;
    var cachedData = self.cache[offset];
    if (!cachedData) {
      rpc('get_bookings', {
        building_id: settings.buildingId,
        limit: 12,
        offset: offset
      }).then(function(data) {
        self.setState(data.result, self.updateControls);
        self.cache[offset || 0] = data.result;
      });
    } else {
      self.setState(cachedData, self.updateControls);
    }
  },

  renderMatrix: function () {
    // Be sure the initial state was updated with data already
    if (!this.state.dates) {
      return;
    }

    var self = this;

    var start = this.state.start;
    var end = this.state.end;

    var dates = [];
    var date, day, display, i, lastDay;

    for (i = start; i < end; i += 1) {
      date = moment(this.state.dates[i]);
      day = date.date();
      if (lastDay && lastDay !== day) {
        display = date.format('dd');
      } else {
        display = date.hour() + 'h';
      }
      lastDay = day;
      dates.push(<th style={{textAlign: 'left'}} key={i}>{display}</th>);
    }

    var rows = [];
    _.each(this.state.bookables, function(bookable, index) {
      var row = [];
      var key;
      for (i = start; i < end; i += 1) {
        key = [index, i];
        row.push(
          <Control key={key}
              bookable={bookable.title}
              bookable-id={bookable.id}
              columnId={i + 1}
              date={self.state.dates[i]}
              onClick={self.handleControlClick.bind(self, key)}
              ref={'control-' + key}
              status={bookable.status[i]} />
        );
      }

      rows.push(
        <tr key={index}>
          <th>{bookable.title}</th>
          {row}
        </tr>
      );
    });

    var html = (
      <table className='table booking-matrix'>
        <thead>
          <tr>
            <th></th>
            {dates}
          </tr>
        </thead>
        <tbody>
          {rows}
        </tbody>
      </table>
    );

    return html;
  },

  updateControls: function () {
    var forthButton = $(this.refs.forthButton.getDOMNode());
    var backButton = $(this.refs.backButton.getDOMNode());
    forthButton.attr('disabled', this.state.next < 0);
    backButton.attr('disabled', this.state.prev < 0);

    // Work-around for missing method to modify displayed date w/o triggering dp.change handler
    var input = $(this.refs.date.getDOMNode()).find('input');
    input.val(moment(this.state.dates[0]).startOf('day').format(this.datePicker.format()));

    // Only set the maxDate once
    if (!this.datePicker.maxDate()) {
      var minDate = this.datePicker.minDate();
      var maxDate = minDate.endOf('day').add(this.state.max_booking_days, 'days');
      this.datePicker.maxDate(maxDate);
    }
  },

  handleForthClick: function (event) {
    event.preventDefault();
    if (this.state.next > -1) {
      this.fetch(this.state.next);
    }
  },

  handleBackClick: function (event) {
    event.preventDefault();
    if (this.state.prev > -1) {
      this.fetch(this.state.prev);
    }
  },

  handleControlClick: function (key) {
    var control = this.refs['control-' + key];
    if (!control.isOutdated() && !control.isAssigned()) {
      var bookableId = key[0];
      var bookingId = key[1];
      var bookable = this.state.bookables[bookableId];
      var status = bookable.status[bookingId];
      bookable.status[bookingId] = (status === 1 ? -1 : 1);
      this.setState(this.state);
    }
  },

  handleSubmit: function (event) {
    event.preventDefault();

    var self = this;
    var target = $(event.target).attr('disabled', true);
    var bookables = _.without(_.flatten(_.pluck(this.cache, 'bookables')), undefined);
    var joinedBookables = [];

    bookables.forEach(function(bookable) {
      var joinedBookable = joinedBookables[bookable.id];
      if (!joinedBookable) {
        joinedBookables[bookable.id] = bookable;
      } else {
        joinedBookable.status = joinedBookable.status.concat(bookable.status);
      }
    });

    var bookings = {
      dates: _.without(_.flatten(_.pluck(this.cache, 'dates')), undefined),
      bookables: _.without(joinedBookables, undefined)
    };

    var param = {
      bookings: bookings,
      building_id: settings.buildingId
    };

    rpc('update_bookings', param).done(function (result) {
      $(document).trigger('status', {
        type: 'success',
        content: 'Ihre Reservierung wurde übernommen.'
      });
      wait(1000).then(function() {
        $(document).trigger('modal', {display: false});
      });
    }).fail(function() {
      var offset = self.state.prev + 1;
      self.setState(self.getInitialState(), function() {
        self.cache = [];
        self.fetch(offset);
        target.attr('disabled', false);
      });
    });
  }
});

var Control = React.createClass({
  render: function () {
    var label = <i className='glyphicon glyphicon-plus selected'/>;
    var labelClass = ['booking-checkbox'];
    var tdClass = '';
    var isOutdated = this.isOutdated();

    if (isOutdated) {
      tdClass = 'disabled';
      label = <i className='glyphicon glyphicon-ban-circle'/>;
      labelClass.push('ghost', tdClass);
    }

    if (this.props.status === 1) {
      label = <i className='glyphicon glyphicon-plus'/>;
      labelClass.push('text-success');
    } else if (this.isAssigned()) {
      if (!this.props.status) {
        label = <i className='glyphicon glyphicon-ban-circle'/>;
      } else {
        label = <small>{this.props.status}</small>;
      }
      tdClass = 'disabled';
      labelClass.push('text-danger', tdClass);
    } else if (!isOutdated) {
      labelClass.push('invisible');
    }

    return (
      <td onClick={this.props.onClick} className={tdClass + ' col-' + this.props.columnId}>
        <label className={_.uniq(labelClass).join(' ')}>
          {label}
        </label>
      </td>
    );
  },

  isAssigned: function () {
    return _.isString(this.props.status);
  },

  isOutdated: function () {
    var now = new Date();
    return new Date(this.props.date) - now < 0;
  },

  handleClick: function (event) {
    event.preventDefault();
  }
});

module.exports = Matrix;

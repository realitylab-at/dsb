'use strict';

function Scheduler(name, interval, func) {
  name = (name || 'Scheduler-' + Date.now());
  interval = (interval || 1000);
  func = (func || function() {});

  var self = this;
  var id = null;

  var runner = function() {
    //console.info('Running scheduler “%s”', self.name);
    func.call(self);
    self.lastRun = new Date();
    return runner;
  };

  this.name = name;
  this.lastRun = 0;

  this.isRunning = function() {
    return !!id;
  };

  this.start = function() {
    if (!this.isRunning()) {
      console.info('Starting scheduler “%s”', this.name);
      id = setInterval(runner(), interval);
    }
    return this;
  };

  this.stop = function() {
    if (this.isRunning()) {
      console.info('Stopping scheduler “%s”', this.name);
      id = clearInterval(id);
    }
    return this;
  };

  this.dispose = function() {
    this.stop();
    console.info('Disposing scheduler “%s”', this.name);
    return null;
  };

  return this;
}

module.exports = Scheduler;

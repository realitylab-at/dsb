'use strict';

var _ = require('lodash');
var $ = require('jquery');
var React = require('react');
var sprintf = require('./utils').sprintf;

var Upload = React.createClass({
  getInitialState: function() {
    return {
      files: [],
      errors: []
    };
  },

  render: function() {
    return (
      <div className='form-group'>
        <label className='control-label'>Bild</label>
        <div className='col-md-8 fileinput input-group fileinput-new' data-provides='fileinput'>
          <div className='form-control' data-trigger='fileinput' style={{'whiteSpace': 'nowrap',overflow: 'hidden'}}>
            <span id='input-file' className='fileinput-filename' readOnly ref='filename'></span>
          </div>
          <span className='input-group-addon btn btn-default btn-file'>
            <span className='fileinput-new'>
              <i className='glyphicon glyphicon-picture'></i>
            </span>
            <span className='fileinput-exists'>
              <i className='glyphicon glyphicon-picture'></i>
            </span>
            <input type='file' ref='fileinput'/>
          </span>
          <a href='javascript:' className='input-group-addon btn btn-default fileinput-exists' data-dismiss='fileinput' ref='dismiss'>
            <i className='glyphicon glyphicon-remove'></i>
          </a>
          <div className='clearfix' />
        </div>
      </div>
    );
  },

  componentDidMount: function() {
    var self = this;
    var fileInput = this.refs.fileinput.getDOMNode();

    FileAPI.event.on(fileInput, 'change', function(event) {
      var name = $(this).val().replace(/\\/g, '/').replace(/.*\//, '');
      $(self.refs.filename.getDOMNode()).html(name);
      self.validate(this, event);
    });

    $(this.refs.dismiss.getDOMNode()).on('click', function () {
      $(document).trigger('status', null);
    });
  },

  validate: function(input, event) {
    var self = this;
    var id = this.refs.filename.getDOMNode().id;
    var errors = [];
    var files = FileAPI.getFiles(input);
    FileAPI.filterFiles(files, function(file, info) {
      var error = {refId: id};
      if (/image/.test(file.type)) {
        if (info && (info.width < 100 || info.width > 1000 ||
              info.height < 100 || info.height > 1000)) {
          error.text = sprintf('Bitte wählen Sie ein Bild mit mind. 100&times;100 und höchstens 1000&times;1000 Pixel.');
        } else if (file.size > 1 * FileAPI.MB) {
          error.text = sprintf('Bitte wählen Sie ein Bild mit max. 1 MB.');
        } else {
          return true;
        }
      } else {
        error.text = sprintf('Bitte wählen Sie ein Bild im Format JPEG, PNG oder GIF.');
      }
      errors.push(error);
      return false;
    }, function(result, ignored) {
      $(input).removeData('errors');
      if (result.length > 0) {
        var files = [];
        _.each(result, function(file) {
          FileAPI.readAsDataURL(file, function(event) {
            if (event.type === 'error') {
              $(document).trigger('status', {
                type: 'danger',
                content: {
                  refId: 'input-file',
                  text: 'Der von Ihnen verwendete Browser unterstützt die erforderliche Schnittstelle zum Hochladen von Bildern nicht.'
                }
              });
            } else if (event.type === 'load') {
              files.push(event.result);
              $(document).trigger('status', null);
            }
          });
        });
        self.setState({files: files});
      } else if (ignored.length > 0) {
        $(input).data({errors: errors});
        $(document).trigger('status', {
          type: 'danger',
          content: errors
        });
      }
    });
  }
});

module.exports = Upload;

var config = require('../config.js');

var csso = require('csso');
var less = require('less');
var shell = require('shelljs');

config.sites.forEach(function (site, index) {
  var source = './sites/' + site + '/';
  var dest = config.dest + site + '/';

  console.log('Processing CSS for site %s', site);

  shell.mkdir('-p', dest + 'css');

  var css = shell.cat(
    'node_modules/bootstrap/dist/css/bootstrap.css',
    'node_modules/eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.css',
    'node_modules/jasny-bootstrap/dist/css/jasny-bootstrap.css'
  );

  css.to(dest + 'css/main.css');

  var lessCss = shell.cat('less/main.less', source + 'settings.less');

  less.render(lessCss)
    .then(function(result) {
      result.css.toEnd(dest + 'css/main.css');
      csso.minify(shell.cat(dest + 'css/main.css'))
        .to(dest + 'css/main.min.css');
      console.log('Finished building CSS for site %s', site);
    });

});

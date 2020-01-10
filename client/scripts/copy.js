var config = require('../config.js');

var shell = require('shelljs');

config.sites.forEach(function (site, index) {
  var source = 'sites/' + site + '/';
  var dest = config.dest + site + '/';

  shell.mkdir('-p', dest);
  shell.cp('-f', 'index.html', dest + 'index.html');

  shell.cp('-fR', 'img', dest);
  shell.cp('-f', source + 'img/*', dest + 'img');

  shell.cp('-fR', 'fonts', dest);

  shell.mkdir('-p', dest + 'js/compat');
  shell.cp('-f', 'node_modules/html5shiv/dist/html5shiv.min.js',
    dest + 'js/compat/html5shiv.min.js');
  shell.cp('-f', 'node_modules/respond.js/dest/respond.min.js',
    dest + 'js/compat/respond.min.js');
  shell.cp('-fR', 'node_modules/bootstrap/dist/fonts/*', dest + 'fonts');

  shell.cp('-fR', 'node_modules/webshim/js-webshim/minified/shims', dest + 'js');
  shell.cp('-fR', 'node_modules/fileapi/dist', dest + 'js/file-api');
});

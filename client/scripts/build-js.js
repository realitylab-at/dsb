var config = require('../config.js');

var browserify = require('browserify');
var fs = require('fs');
var minify = require('uglify-js').minify;
var shell = require('shelljs');

config.sites.forEach(function (site, index) {
  var source = './sites/' + site + '/';
  var dest = config.dest + site + '/';

  console.log('Processing JavaScript for site %s', site);

  shell.mkdir('-p', dest + 'js');
  shell.cat(source + 'settings.js').to(dest + 'js/main.js');

  var writeStream = fs.createWriteStream(dest + 'js/main.js', {flags: 'a'});

  writeStream.on('finish', function() {
    var minified = minify(dest + 'js/main.js');
    fs.writeFile(dest + 'js/main.min.js', minified.code, function() {
      console.log('Finished building JavaScript for site %s', site);
    });
  });

  var app = browserify();
  app.add('./js/main.js');

  app.bundle()
    .pipe(writeStream);
});

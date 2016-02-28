'use strict';

var express = require('express');
var request = require('request')
var app = express();

app.use('/*', function(req, res) {
	req.pipe(request('http://localhost:8888/' + req.params[0])).pipe(res);	
});

if (require.main == module) {
	app.listen(3000, function() {
		console.log('Express server listening on port ' + this.address().port);
	});
} else {
	module.exports = app;
}

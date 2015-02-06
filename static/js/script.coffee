'use strict'
$ ->
	$('#logout').click ->
		document.cookie = ''
		window.location.href = '/login'
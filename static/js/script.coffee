'use strict'
$ ->
	$('#logout').click ->
		document.cookie = 'username=null; expires=Thu, 01 Jan 1970 00:00:01 GMT;'
		document.cookie = 'password=null; expires=Thu, 01 Jan 1970 00:00:01 GMT;'
		location.href = '/login'

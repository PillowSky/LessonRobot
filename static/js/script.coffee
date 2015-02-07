'use strict'
$ ->
	$('#logout').click ->
		document.cookie = 'username=null; expires=Thu, 01 Jan 1970 00:00:01 GMT;'
		document.cookie = 'password=null; expires=Thu, 01 Jan 1970 00:00:01 GMT;'
		location.href = '/login'

	window.learning = false
	$('.learnButton').click ->
		if window.learning
			alert('已经学得很快了，就一门门学吧')
		else
			window.learning = true
			self = this
			courseID = $(this).attr('target')
			$(this).addClass('disabled').text('需要15秒...')
			$.post '/learn', {"courseID": courseID}, (data)->
				$(self).removeClass('btn-primary').removeClass('btn-info')
				window.learning = false
				if data == 'ok'
					$(self).addClass('btn-success').text('学习成功')
				else
					$(self).removeClass('disabled').addClass('btn-warning').text('重新学习')

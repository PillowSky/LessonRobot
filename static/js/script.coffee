'use strict'
$ ->
	$('#logout').click ->
		document.cookie = 'username=null; expires=Thu, 01 Jan 1970 00:00:01 GMT;'
		document.cookie = 'password=null; expires=Thu, 01 Jan 1970 00:00:01 GMT;'
		location.href = '/login'

	window.queue = []
	window.learning = false

	$('.learnButton').click ->
		$(this).addClass('disabled').text('队列中...')
		window.queue.push([$(this).attr('target'), $(this)])
		processQueue()

	processQueue = ->
		if window.queue.length and not window.learning
			window.learning = true
			[courseID, node] = window.queue.shift()
			node.text('需要15秒...')

			$.post '/learn', {"courseID": courseID}, (data)->
				node.removeClass('btn-primary').removeClass('btn-info')
				if data == 'ok'
					node.addClass('btn-success').text('学习成功')
				else
					node.removeClass('disabled').addClass('btn-warning').text('重新学习')
				window.learning = false
				processQueue()

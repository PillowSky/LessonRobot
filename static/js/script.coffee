'use strict'
$ ->
	queue = []
	learning = false

	$('.learnButton').click ->
		$(this).addClass('disabled').text('队列中...')
		queue.push([$(this).attr('target'), $(this)])
		processQueue()

	processQueue = ->
		if queue.length and not learning
			learning = true
			[courseID, node] = queue.shift()
			node.text('学习中...')

			$.post '/learn', {"courseID": courseID}, (data)->
				node.removeClass('btn-primary').removeClass('btn-info')
				if data == 'ok'
					node.addClass('btn-success').text('学习成功')
				else
					node.removeClass('disabled').addClass('btn-warning').text('重新学习')
				learning = false
				processQueue()

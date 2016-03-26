import json
import requests
from pyquery import PyQuery

url = 'http://jhce.jhxf.gov.cn/Forum/showuser.aspx?page='
cookies = {
	'dnt': 'userid=719&password=KdRQnUp7vxobZZw2EuNt1rcYeWfOesptEnZvy59D6wK7702T0kqPGg%3d%3d&avatar=avatars%5ccommon%5c0.gif&tpp=0&ppp=0&pmsound=1&invisible=0&referer=index.aspx&sigstatus=0&expires=-1&visitedforums=2'
}

name_list = []

for i in range(300, 391):
	print(i)
	d = PyQuery(requests.get(url + str(i), cookies=cookies).text)
	d('.mainbox a.bold').each(lambda i, e: name_list.append(e.text))

with open('accounts_390.json', 'w') as fout:
	fout.write(json.dumps(name_list))

print('All done')
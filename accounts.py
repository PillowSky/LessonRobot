import json
from pyquery import PyQuery

url = 'http://www.sygj.org.cn/forum/showuser.aspx?page='
name_list = []

for i in range(1, 49+1):
	print(i)
	d = PyQuery(url + str(i))
	d('.datatitle a').each(lambda i, e: name_list.append(e.text))

with open('accounts.json', 'w') as fout:
	fout.write(json.dumps(name_list))

print('All done')
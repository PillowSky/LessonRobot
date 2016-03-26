import json
from pymongo import MongoClient

mongoUrl = "mongodb://localhost/region"
region = MongoClient(mongoUrl)['region']['region']

cursor = region.find({'domain':'www.lsce.gov.cn'})

accounts = []

for document in cursor:
	accounts.append(document['username'])

with open('accounts.json', 'w') as fout:
	fout.write(json.dumps(accounts))

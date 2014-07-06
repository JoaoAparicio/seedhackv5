from flask import Flask
app = Flask(__name__)
from flask import request

from pymongo import MongoClient
client = MongoClient()
db = client.clarity
events = db.events
from pymongo.errors import InvalidDocument
users = db.users

import json

# Method one
#from bson.objectid import ObjectId
#idA = ObjectId()
#print(idA)

@app.route('/users/', methods = ['POST'])
def refresh_token():
    r = request.json
    print r
    if 'id' not in r.keys():
        return 'NO ID', 400
    u = users.find({'id':r['id']}).count()
    if u:
#        print r['id']
#        print r
        users.update({'id':r['id']}, {'$set' : r})
#        users.find_and_modify(query={'id',r['id']}, update={'$set', {'a':'b'}})
        return 'UPDATED', 200
    else:
        users.insert(r)
        return 'INSERTED', 200

@app.route("/")
def hello():
    return "Hello World!"

def push_to_db(item):
    try:
        events.insert(item)
    except (TypeError, InvalidDocument) as inst:
        print 'ERROR', inst

@app.route('/post/', methods = ['POST'])
def save_post():
    r = request.json
    if type(r) == type([]):
#        print 'list'
        for item in r:
            print item
            push_to_db(item)
    elif type(r) == type({}):
        print r
        events.insert(r)

#        try:
#            xpto = events.put(r)
#            print xpto
#        except Exception as inst:
#            print type(inst)
    else:
        print 'nope'
    return 'OK', 200

from collections import defaultdict

@app.route('/websites/', methods = ['POST'])
def get_websites():
    d = defaultdict(int)
    v = defaultdict(int)
    websites = events.find({'$and':[{'platform':'chrome'},{'timestamp':{'$gt':start}},{'timestamp':{'$lt':end}}]})
    for w in websites:
        d[w['process_name']] += w['data']['duration']
        v[w['process_name']] += 1
    return json.dumps({'duration':d, 'visits':v}), 200


@app.route('/communication/', methods = ['POST'])
def get_communication():
    r = request.json
    start = r['start']
    end = r['end']
#    print start, end
    calls = events.find({'$and':[{'process_name':'call_log'},{'timestamp':{'$gt':start}},{'timestamp':{'$lt':end}}]})
#    print calls
    n_phone_calls = calls.count()
#    print n_phone_calls
    d = defaultdict(int)
    d['ads'] += 1
    for c in calls:
#        print c
        if 'person_name' in c['data']:
#            print ['data']['person_name']
            d[c['data']['person_name']] += 1
        else:
#            print ['data']['person_number']
            d[c['data']['person_number']] += 1
#    print d
    return json.dumps({'n_phone_calls':n_phone_calls, 'top':d}), 200
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=False)




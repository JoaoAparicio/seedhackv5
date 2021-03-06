from flask import Flask
app = Flask(__name__)
from flask import request

from pymongo import MongoClient
client = MongoClient()
db = client.clarity
events = db.events
from pymongo.errors import InvalidDocument
users = db.users

import json, re
import datetime, time

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
    us = users.find_one({'id':r['id']})
#    u = us.count()
    if us:
#        print r['id']
#        print r
        users.update({'id':r['id']}, {'$set' : r})
#        users.find_and_modify(query={'id',r['id']}, update={'$set', {'a':'b'}})
        del us['_id']
        return json.dumps(us), 200
    else:
        del us['_id']
        return json.dumps(us), 200

@app.route("/")
def hello():
    return "Hello World!"

def push_to_db(item):
    try:
        events.insert(item)
    except (TypeError, InvalidDocument) as inst:
        print 'ERROR', inst


MAGIC_TEXT = 'lets meet the day after'
MAGIC_ID = ''
def cheat_move(r):
    one = events.find_one({'$and':[{'platform':'calendar'},{'id':MAGIC_ID}]})
    one.update({'_id':ObjectId(one['_id'])}, {'$set':{'timestamp':one['timestamp']+86400000}})

@app.route('/post/', methods = ['POST'])
def save_post():
    r = request.json

    if re.search(MAGIC_TEXT,r['data']['body']):
        cheat_move(r)
        return 'OK', 200

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
    r = request.json
    start = r['start']
    end = r['end']
    d = defaultdict(int)
    v = defaultdict(int)
    websites = events.find({'$and':[{'platform':'chrome'},{'timestamp':{'$gt':start}},{'timestamp':{'$lt':end}}]})
    for w in websites:
        d[w['process_name']] += w['data']['duration']
        v[w['process_name']] += 1
        fvico[w['process_name']] = w['data']['favIconUrl']
    res = {}
    for website in d.keys():
        res[website] = [v[website], d[website], fvico[website]]

#    return json.dumps({'duration':d, 'visits':v}), 200
    return json.dumps(res), 200


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
    duration = defaultdict(int)
    d['ads'] += 1
    for c in calls:
#        print c
        if 'person_name' in c['data']:
#            print ['data']['person_name']
            d[c['data']['person_name']] += 1
            duration[c['data']['person_name']] += int(c['data']['duration'])
        else:
#            print ['data']['person_number']
            d[c['data']['person_number']] += 1
            duration[c['data']['person_number']] += int(c['data']['duration'])
#    print d
    txts = events.find({'$and':[{'process_name':'sms_log'},{'timestamp':{'$gt':start}},{'timestamp':{'$lt':end}}]})
    n_txts = defaultdict(int)
    for t in txts:
        n_txts[t['data']['address']] += 1
    total_txts =sum (  n_txts.values() )

    res = {}
    for p in d.keys():
        res[p] = [d[p], duration[p]]
#    return json.dumps({'n_phone_calls':n_phone_calls, 'calls':d, 'duration':duration, 'n_txts':n_txts}), 200
    return json.dumps({'n_phone_calls':n_phone_calls, 'calls':res, 'n_txts':n_txts, 'total_txts':total_txts}), 200

def convert_date_to_timestamp(start):
    if 'dateTime' in start.keys():
        dt = start['dateTime']
        if len(dt.split('+'))==2:
            timestamp = time.mktime(datetime.datetime.strptime(dt.split('+')[0], '%Y-%m-%dT%H:%M:%S').timetuple())
            timestamp = str( int(timestamp) + 3600 ) + '000'
            return timestamp
        if len(dt.split('Z')) ==2:
            timestamp = time.mktime(datetime.datetime.strptime(dt.split('Z')[0], '%Y-%m-%dT%H:%M:%S').timetuple())
            timestamp = str( int(timestamp) ) + '000'
            return timestamp
    if 'date' in start.keys():
        dt = start['date']
        timestamp = time.mktime(datetime.datetime.strptime(dt.split('.')[0], '%Y-%m-%d').timetuple())
        timestamp = str( int(timestamp) ) + '000'
        return timestamp

@app.route('/calendar/', methods = ['POST'])
def get_calendar():
    r = request.json
    start = r['start']
    end = r['end']
    cal_events = events.find({'$and':[{'platform':'calendar'},{'timestamp':{'$gt':start}},{'timestamp':{'$lt':end}}]})
    res = []
    for item in cal_events:
        new_item = {}
        for type_e in ['meet', 'event', 'skype']:
            if re.search(type_e, item['summary'].lower()):
                new_item['type'] = type_e
            if 'type' not in new_item.keys():
                new_item['type'] = 'meet'
        for tag in ['industryx', 'fintech', 'techcity']:
            if re.search(tag, item['summary'].lower()):
                new_item['tag'] = tag
            if 'tag' not in new_item.keys():
                new_item['tag'] = ''
        new_item['tag'] = new_item['type'] + ' ' + new_item['tag']
        del new_item['type']
        new_item['startTime'] = convert_date_to_timestamp(item['data']['start'])
        new_item['endTime'] = convert_date_to_timestamp(item['data']['end'])
        new_item['title'] = item['data']['summary']
        res.append(new_item)
    return json.dumps(res), 200

         

@app.route('/calendarfeed/', methods= ['POST'])
def get_calendarfeed():

    text_duration = 1000 * 60
    
    js = request.json

    start = js['start']
    end= js['end']

    android = events.find({'$and': [{'platform':'android'},{'timestamp':{'$gt':start}},{'timestamp':{'$lt':end}}]})
    
    final_json = []

    for item in android:
        ev_title = ""
        ev_start = 0
        ev_end = 0
        ev_tag = "__"

        if item['process_name'] == 'call_log':
            ev_title = "Call with "
            if item['data']['process_type'] == 'missed':
                ev_title = "Missed call from "
            if 'person_name' in item['data']:
                ev_title = ev_title + item['data']['person_name']
            else:
                ev_title = ev_title + item['data']['person_number']

            ev_start = int(item['timestamp'])
            ev_end = ev_start + max(int(item['data']['duration']), text_duration)
            ev_tag="call"
        elif item['process_name'] == 'sms_log':
            ev_title = "Text to " + item['data']['address']
            if item['data']['process_type'] == "received":
                ev_title = "Text from " + item['data']['address']
            ev_start = int(item['timestamp'])
            ev_end = ev_start + text_duration
            ev_tag = "sms"

        final_json.append({
            "startTime": ev_start,
            "endTime": ev_end,
            "title": ev_title,
            "tag": ev_tag,
        })

    print json.dumps(final_json)
    return json.dumps(final_json)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)


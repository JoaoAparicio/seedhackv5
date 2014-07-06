from flask import Flask
app = Flask(__name__)
from flask import request

from pymongo import MongoClient
client = MongoClient()
db = client.clarity
events = db.events2
from pymongo.errors import InvalidDocument
users = db.users


# Method one
#from bson.objectid import ObjectId
#idA = ObjectId()
#print(idA)

@app.route('/users/', methods = ['POST'])
def refresh_token():
    r = request.json
    if 'id' not in r.keys():
        return 'NO', 400
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
        print 'list'
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
     
    
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)




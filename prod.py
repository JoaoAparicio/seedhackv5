from flask import Flask
app = Flask(__name__)
from flask import request

from pymongo import MongoClient
client = MongoClient()
db = client.clarity
events = db.events
from pymongo.errors import InvalidDocument

# Method one
#from bson.objectid import ObjectId
#idA = ObjectId()
#print(idA)

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/post/', methods = ['POST'])
def save_post():
    r = request.json
    if type(r) == type([]):
        for item in r:
#            events.insert(item)
            try:
                events.insert(item)
            except (TypeError, InvalidDocument) as inst:
                print inst
                pass
    elif type(r) == type({}):
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
    app.run(host='0.0.0.0', port=80, debug=True)




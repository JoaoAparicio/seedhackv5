from flask import Flask
app = Flask(__name__)
from flask import request, render_template

from pymongo import MongoClient
client = MongoClient()
db = client.clarity
events = db.events

# Method one
#from bson.objectid import ObjectId
#idA = ObjectId()
#print(idA)

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/login/', methods = ['GET', 'POST'])
def login_func():
    if request.method == 'GET':
        return render_template('login.html')
        try:
            return render_template('login.html')
        except Exception as inst:
            print type(inst)
    if request.method == 'POST':
        return 'OK', 200


@app.route('/post/', methods = ['POST'])
def save_post():
    r = request.json
    if type(r) == type([]):
        print 'list'
        for item in r:
            events.insert(item)
    elif type(r) == type({}):
        print r, type(r)
        events.insert(r)
    else:
        print 'nope'
    return 'OK', 200
     
    
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)




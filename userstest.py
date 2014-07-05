import json, urllib2, requests

#data = {
#        'ids': [12, 3, 4, 5, 6]
#}
#req = urllib2.Request('http://ec2-54-213-238-96.us-west-2.compute.amazonaws.com/post/')
#req.add_header('Content-Type', 'application/json')
#response = urllib2.urlopen(req, json.dumps(data))

url = "http://ec2-54-213-238-96.us-west-2.compute.amazonaws.com:8080/users/"
#url = "http://ec2-54-213-238-96.us-west-2.compute.amazonaws.com:80/users/"
#data = {'access_token': 'asd', 'refresh_token': 'asd', 'id': 'my_id', 'email':'asdasd@gmail.com', 'given_name':'asd', 'family_name':'asd', 'link':'asd', 'picture':'asd', 'gender':'asd', 'locale':'asd'}
data = {'access_token': 'new_access_token', 'refresh_token': 'nice', 'id': 'my_id', 'email':'asdasd@gmail.com', 'given_name':'asd', 'family_name':'asd', 'link':'asd', 'picture':'asd', 'gender':'asd', 'locale':'asd'}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
r = requests.post(url, data=json.dumps(data), headers=headers)


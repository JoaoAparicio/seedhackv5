# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Command-line skeleton application for Calendar API.
Usage:
  $ python sample.py

You can also get help on all the command-line flags the program understands
by running:

  $ python sample.py --help

"""

import time, datetime
import argparse
import httplib2
import os
import sys

from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools

# Parser for command-line arguments.
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])


# CLIENT_SECRETS is name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret. You can see the Client ID
# and Client secret on the APIs page in the Cloud Console:
# <https://cloud.google.com/console#/project/421139284824/apiui>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')
print CLIENT_SECRETS

# Set up a Flow object to be used for authentication.
# Add one or more of the following scopes. PLEASE ONLY ADD THE SCOPES YOU
# NEED. For more information on using scopes please see
# <https://developers.google.com/+/best-practices>.
FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
  scope=[
      'https://www.googleapis.com/auth/calendar',
      'https://www.googleapis.com/auth/calendar.readonly',
    ],
    message=tools.message_if_missing(CLIENT_SECRETS))

import re

#no_time_counter = 0
######################################################
def cal_item_to_clarity_item(cal_item):
    if cal_item['status'] == 'cancelled':
        return None
    platform = 'calendar'
    try:
        device_name = cal_item['creator']['email']   ## this isnt completely correct!
    except KeyError:
        device_name = ''
    try:
#        t = cal_item['created']
        t = cal_item['start']['dateTime']
    except KeyError:
#        print 'no start date'
#        no_time_counter += 1
        return None
    try:
        timestamp = time.mktime(datetime.datetime.strptime(t.split('.')[0], '%Y-%m-%dT%H:%M:%S').timetuple())
        timestamp = str( int(timestamp) ) + '000'
    except ValueError:
#        print t
        timestamp = time.mktime(datetime.datetime(1971,1,1).timetuple())
#    timestamp = time.mktime(datetime.datetime.strptime(t.split('.')[0], '%Y-%m-%dT%H:%M:%S').timetuple())
#    timestamp = str( int(timestamp) ) + '000'
    try:  ## sometimes the creator is not there??
        user = cal_item['creator']['displayName']
    except KeyError:
        user = ''
    data = cal_item
    process_id = cal_item.get('id','')
    process_name = cal_item.get('kind','')
    summary = cal_item.get('summary','')
    if re.search('travel', summary.lower()):
        process_type = 'travel'
    else:
        process_type = 'meeting'
    return {'platform':platform,
            'device_name':device_name,
            'timestamp':timestamp,
            'user':user,
            'data':data,
            'process_id':process_id,
            'process_name':process_name,
            'summary':summary}
######################################################

######################################################
import json, requests

# j is a json or a list of jsons
def post_it(j):
    url = "http://ec2-54-213-238-96.us-west-2.compute.amazonaws.com:8080/post/"
#    url = "http://ec2-54-213-238-96.us-west-2.compute.amazonaws.com:80/post/"
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=json.dumps(j), headers=headers)
######################################################

def main(argv):
  # Parse the command-line flags.
  flags = parser.parse_args(argv[1:])

  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # credentials will get written back to the file.
  storage = file.Storage('sample.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(FLOW, storage, flags)

  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with our good Credentials.
  http = httplib2.Http()
  http = credentials.authorize(http)

  # Construct the service object for the interacting with the Calendar API.
  service = discovery.build('calendar', 'v3', http=http)

  try:
    print "Success! Now add code here."
#    r = service.calendarList().list().execute()
#    for i in r['items']:
#        print i

#    calendarlist = ['hello@dotforgeaccelerator.com', 'river@dotforgeaccelerator.com', 'lee@dotforgeaccelerator.com', 'lee.strafford@googlemail.com', 'emma@dotforgeaccelerator.com']
    calendarlist = ['hello@dotforgeaccelerator.com', 'river@dotforgeaccelerator.com', 'lee@dotforgeaccelerator.com', 'lee.strafford@googlemail.com']
    for cId in calendarlist:
        r = service.events().list(calendarId=cId).execute()
        l = map(cal_item_to_clarity_item, r['items'])
        post_it(l)
#    print 'total no time:', no_time_counter
#        for clarityitem in l:
#            if clarityitem:
#                print clarityitem

#    r = service.events().list(calendarId='jpmn.aparicio@gmail.com').execute()
#    print r

#    l = map(cal_item_to_clarity_item, r['items'])
#    post_it(l)

  except client.AccessTokenRefreshError:
    print ("The credentials have been revoked or expired, please re-run"
      "the application to re-authorize")


# For more information on the Calendar API you can visit:
#
#   https://developers.google.com/google-apps/calendar/firstapp
#
# For more information on the Calendar API Python library surface you
# can visit:
#
#   https://developers.google.com/resources/api-libraries/documentation/calendar/v3/python/latest/
#
# For information on the Python Client Library visit:
#
#   https://developers.google.com/api-client-library/python/start/get_started
if __name__ == '__main__':
  main(sys.argv)

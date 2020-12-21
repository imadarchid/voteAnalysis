import requests
import json
from dotenv import load_dotenv
load_dotenv()

import os
client_id = os.environ.get("client-id")
client_secret = os.environ.get("client-secret")
tenant = os.environ.get("tenant")


# Request to Graph API

groups = [{'school': 'SBA Undergraduate', 'grp_id': 'a5f4795f-c7c0-4ecb-b456-2662d9e7c3ce', 'students': [], 'voters': 0}, {'school': 'SBA Graduate', 'grp_id': '290efbaa-3671-472c-b288-1382b363607a', 'students': [], 'voters': 0}, 
{'school': 'SSE Students', 'grp_id': 'd6b30385-1ece-4163-938e-d2da3e53c86e', 'students': [], 'voters': 0}, {'school': 'SHSS Undergraduate', 'grp_id': 'a9c78c8b-b003-490b-8fb5-14defc7291b5', 'students': [], 'voters': 0}, 
{'school': 'SHSS Graduate', 'grp_id': 'eb647ea5-3991-49d4-919a-bf1a6d09d1e6', 'students': [], 'voters': 0}]

def getGroupMembers(group_id, token):
    members = []
    headers = {'Authorization': 'Bearer ' + token}
    r = requests.get('https://graph.microsoft.com/v1.0/groups/' + group_id + '/members', headers=headers)
    r_result = r.json()

    cnt = 0

    if '@odata.nextLink' in r_result:
        try:
            while r_result['@odata.nextLink']:
                for st in r_result['value']:
                    members.append(st)
                r = requests.get(r_result['@odata.nextLink'], headers=headers)
                r_result = r.json()
        except KeyError as k:
            for st in r_result['value']:
                members.append(st)
            print('finished pagination')
            pass
    else:
        for st in r_result['value']:
            members.append(st)
    

    return members

def getToken():
    creds = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default'
    }

    r_token = requests.post('https://login.microsoftonline.com/' + tenant + '/oauth2/v2.0/token', data=creds)
    response_token = r_token.json()
    print('Access Token granted')
    return response_token['access_token']

def extractStudents():
    access_token = getToken()
    for s in groups:
        print('Processing group:' + s['school'])
        grp_members = getGroupMembers(s['grp_id'], access_token)
        s['students'].append(grp_members)

    print('successfully retrieved all students')
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(groups, f, ensure_ascii=False, indent=4)
    
    getVotersBySchool()

def getVotersBySchool():
    # voters.json is an internal dump of all voters, you shall not get this heh ;)
    with open('voters.json') as f:
        voters = json.load(f)

    with open('data.json') as l:
        students = json.load(l)
    
    
    for s in students:
        for j in s['students'][0]:
            for v in voters:
                if (j['id'] == v['office_id']):
                    s['voters'] += 1

    report = []
    for r in students:
        el = {'grp': r['school'], 'count': r['voters']}
        report.append(el)
    
    print(report)



extractStudents()
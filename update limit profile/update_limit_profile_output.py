import itertools
import random
import string
import requests
import pandas as pd
import csv

login_url = "http://34.143.149.203:8086/api/auth/v1/login"
login_credential = {
    "username": "U2FsdGVkX18uHztBVbI8Tz9e4O/PohGPcanl1zCUet0",
    "password": "U2FsdGVkX18uHztBVbI8Tz9e4O/PohGPcanl1zCUet0"
}
update_url = "http://34.143.149.203:8088/api/config/v1/update-limit-profile"
get_limit_profile_summary_url="http://34.143.149.203:8088/api/config/v1/get-limit-profile"
limit_profile_summary_data={
    "limit" :500,
    "offset" : 0}

headers_login = {"Content-Type": "application/json"}
access_token = None
response_login = requests.post(login_url, json=login_credential, headers=headers_login)
json_response_login = response_login.json()
# print(json_response_login)
if json_response_login.get("isSuccess") == True:
    access_token = json_response_login.get("data", {}).get("access_token", "")
# print(access_token)
headers_limit_profile_summary = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}

response_limit_profile_summary= requests.post(get_limit_profile_summary_url, json=limit_profile_summary_data, headers=headers_limit_profile_summary)
# print(response_lookup_summary)
json_response_limit_profile_summary = response_limit_profile_summary.json()
json_response_limit_profile_summary= json_response_limit_profile_summary.get("values", {}).get("datas", "")
print(json_response_limit_profile_summary)
existing_ids = [item['id'] for item in json_response_limit_profile_summary]
print(existing_ids)   

if access_token:
    headers_update = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}
    with open('update limit profile\input_update_limit_profile.csv', 'r', newline='') as create_file, \
         open('update limit profile\output_update_limit_profile.csv', 'w', newline='', encoding='utf-8') as output_file:
        update = csv.DictReader(create_file)
        fieldnames = ['ID', 'update_id', 'expectation', 'isSuccess', 'code', 'message']
        output_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        output_writer.writeheader()
        id_counter = 1
        # print(create_lookup)
        for row in update:
            data = {key: row[key] for key in row if key not in [ 'ID', 'c_response', 'Error Message']}
            data1={}
            for key, value in data.items():
                if key=="update_id":
                    data1['id']=value
                else:
                    data1[key]=value
            # print(data1)
            print(row.get("update_id", ""))
            response_update = requests.put(update_url, json=data1, headers=headers_update)
            # print(response_update)
            json_response_update = response_update.json()
            update_success = json_response_update.get("isSuccess")
            # print(json_response_update)
            c_response = row.get("c_response")
            print(update_success, c_response)
            if(str(update_success) == str(c_response)):
                 expectation = True
            else:
                expectation= False
            if expectation and c_response == 'True' or expectation and c_response == 'False':
                a_message = "Backend response:"+ json_response_update.get("message", "")
            else:
                a_message = row.get("Error Message", "Unknown Error")
            
            output_row = {
                 "ID": id_counter,
                "expectation": expectation,
                "update_id": row.get("update_id", ""),
                "isSuccess": json_response_update.get("isSuccess", ""),
                "code": json_response_update.get("code", ""),
                "message": a_message,
            }
            output_writer.writerow(output_row)
            id_counter += 1   
            print(id_counter)       
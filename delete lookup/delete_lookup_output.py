import requests
import pandas as pd
import csv

login_url = "...login url..."
login_credential = {
    "username": "username",
    "password": "password"
}

get_lookup_summary_url="...get-lookup-summary url..."
delete_url = "...delete-lookup url..."

lookup_summary_data={
                    "limit" :500,
                    "offset" : 0
                    }

headers_login = {"Content-Type": "application/json"}
access_token = None
response_login = requests.post(login_url, json=login_credential, headers=headers_login)
json_response_login = response_login.json()
print(json_response_login)
if json_response_login.get("isSuccess") == True:
    access_token = json_response_login.get("data", {}).get("access_token", "")
headers_lookup_summary = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}

response_lookup_summary= requests.post(get_lookup_summary_url, json=lookup_summary_data, headers=headers_lookup_summary)
json_response_lookup_summary = response_lookup_summary.json()
json_response_lookup_summary= json_response_lookup_summary.get("values", {}).get("datas", "")
existing_ids = [item['id'] for item in json_response_lookup_summary]
    
if access_token:
    headers_delete = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}
    with open('delete lookup\input_delete_lookup.csv', 'r', newline='') as create_file, \
         open('delete lookup\output_delete_lookup.csv', 'w', newline='', encoding='utf-8') as output_file:
        delete = csv.DictReader(create_file)
        fieldnames = ['ID', 'delete_id', 'expectation', 'isSuccess', 'code', 'message']
        output_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        output_writer.writeheader()
        id_counter = 1
        # print(create_lookup)
        for row in delete:
            data = {key: row[key] for key in row if key not in [ 'ID', 'c_response', 'Error Message']}
            print(data)
            data1={}
            for key, value in data.items():
                if key=="delete_id":
                    data1['id']=value
        
            print(data1)
            # print(row.get("update_id", ""))
            response_delete = requests.post(delete_url, json=data1, headers=headers_delete)
            # print(response_update)
            json_response_delete = response_delete.json()
            delete_success = json_response_delete.get("isSuccess")
            print(json_response_delete)
            c_response = row.get("c_response")
            print(delete_success, c_response)
            if(str(delete_success) == str(c_response)):
                 expectation = True
            else:
                expectation= False
            if expectation and c_response == 'True' or expectation and c_response == 'False':
                a_message = "Backend response:"+ json_response_delete.get("message", "")
            else:
                a_message = row.get("Error Message", "Unknown Error")
            
            output_row = {
                "ID": id_counter,
                "expectation": expectation,
                "delete_id": row.get("delete_id", ""),
                "isSuccess": json_response_delete.get("isSuccess", ""),
                "code": json_response_delete.get("code", ""),
                "message": a_message,
            }
            output_writer.writerow(output_row)
            id_counter += 1   
            print(id_counter)      
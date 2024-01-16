import requests
import csv

success_responses_login = []
fail_responses_login = []
success_responses_create = []
fail_responses_create = []
a_responses_create = []
b_responses_create = []

login_url = "http://34.143.149.203:8086/api/auth/v1/login"
create_limit_profile_url = "http://34.143.149.203:8088/api/config/v1/create-limit-profile"
login_credential = {
    "username": "U2FsdGVkX18uHztBVbI8Tz9e4O/PohGPcanl1zCUet0",
    "password": "U2FsdGVkX18uHztBVbI8Tz9e4O/PohGPcanl1zCUet0"
}

headers_login = {"Content-Type": "application/json"}

access_token = None
response_login = requests.post(login_url, json=login_credential, headers=headers_login)
json_response_login = response_login.json()

if json_response_login.get("isSuccess") == True:
    access_token = json_response_login.get("data", {}).get("access_token", "")
    success_responses_login.append(json_response_login)
else:
    fail_responses_login.append(json_response_login)
    
if access_token:
    headers_create_limit = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}
    with open('create limit profile\input_create_limit_profile.csv', 'r', newline='') as create_file, \
         open('create limit profile\output_create_limit_profile.csv', 'w', newline='', encoding='utf-8') as output_file:
        
        create_limit = csv.DictReader(create_file)

        fieldnames = ['ID', 'expectation', 'isSuccess', 'code', 'message', 'name', 'description',
                        'tps']
        output_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        output_writer.writeheader()
        id_counter = 1
        # print(create_lookup)
        for row in create_limit:
            data = {key: row[key] for key in row if key not in [ 'ID', 'c_response', 'Error Message']}
            print(data)
            response_create_limit = requests.post(create_limit_profile_url, json=data, headers=headers_create_limit)
            # print(response_create_limit)
            json_response_create_limit = response_create_limit.json()
            create_success = json_response_create_limit.get("isSuccess")
            c_response = row.get("c_response")
            print(create_success, c_response)
            if(str(create_success) == str(c_response)):
                expectation = True
            else:
                expectation= False
            if expectation and c_response == 'True' or not expectation and c_response == 'True':
                a_message = "Backend response:"+ json_response_create_limit.get("message", "")
            else:
                a_message = row.get("Error Message", "Unknown Error")
            
            output_row = {
                "ID": id_counter,
                "expectation": expectation,
                "isSuccess": json_response_create_limit.get("isSuccess", ""),
                "code": json_response_create_limit.get("code", ""),
                "message": a_message,
                "name": row.get("name", "") if not create_success else "",
                "description": row.get("description", "") if not create_success else "",
                "tps": row.get("tps", "") if not create_success else "",
            }
            output_writer.writerow(output_row)
            id_counter += 1           
            
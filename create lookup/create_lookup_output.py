import requests
import csv

success_responses_login = []
fail_responses_login = []
success_responses_create = []
fail_responses_create = []
a_responses_create = []
b_responses_create = []

login_url = "...login url..."
create_lookup_url = "...create-lookup url..."
login_credential = {
    "username": "username",
    "password": "password"
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
    headers_create = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}
    with open('create lookup\input_create_lookup.csv', 'r', newline='') as create_file, \
         open('create lookup\output_create_lookup.csv', 'w', newline='', encoding='utf-8') as output_file:
        
        create_lookup = csv.DictReader(create_file)

        fieldnames = ['ID', 'Expectation', 'isSuccess', 'code', 'message', 'type', 'data_code',
                        'value', 'value_unicode', 'data_type']
        output_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        output_writer.writeheader()
        id_counter = 1
        # print(create_lookup)
        for row in create_lookup:
            data = {key: row[key] for key in row if key not in [ 'ID', 'c_response', 'Error Message']}
            # print(data)
            response_create = requests.post(create_lookup_url, json=data, headers=headers_create)
            # print(response_create)
            json_response_create = response_create.json()
            create_success = json_response_create.get("isSuccess")
            c_response = row.get("c_response")
            # print(create_success, c_response)
            if(str(create_success) == str(c_response)):
                expectation = True
            else:
                expectation= False
            if expectation and c_response == 'True' or expectation and c_response == 'False':
                a_message = "Backend response:"+ json_response_create.get("message", "")
            else:
                a_message = row.get("Error Message", "Unknown Error")

            output_row = {
                "ID": id_counter,
                "Expectation": expectation,
                "isSuccess": json_response_create.get("isSuccess", ""),
                "code": json_response_create.get("code", ""),
                "message": a_message,
                "type": row.get("type", "") if not create_success else "",
                "data_code": row.get("code", "") if not create_success else "",
                "value": row.get("value", "") if not create_success else "",
                "value_unicode": row.get("value_unicode", "") if not create_success else "",
                "data_type": row.get("data_type", "") if not create_success else "",
               
            }
            output_writer.writerow(output_row)
            id_counter += 1          
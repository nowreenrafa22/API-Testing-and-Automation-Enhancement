import random
import requests
import pandas as pd

login_url = "http://34.143.149.203:8086/api/auth/v1/login"
login_credential = {
    "username": "U2FsdGVkX18uHztBVbI8Tz9e4O/PohGPcanl1zCUet0",
    "password": "U2FsdGVkX18uHztBVbI8Tz9e4O/PohGPcanl1zCUet0"
}

get_lookup_summary_url="http://34.143.149.203:8088/api/config/v1/get-lookup-summary"
lookup_summary_data={
    "limit" :500,
    "offset" : 0}

headers_login = {"Content-Type": "application/json"}
access_token = None
response_login = requests.post(login_url, json=login_credential, headers=headers_login)
json_response_login = response_login.json()
print(json_response_login)
if json_response_login.get("isSuccess") == True:
    access_token = json_response_login.get("data", {}).get("access_token", "")
# print(access_token)
headers_lookup_summary = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}

response_lookup_summary= requests.post(get_lookup_summary_url, json=lookup_summary_data, headers=headers_lookup_summary)
print(response_lookup_summary)

json_response_lookup_summary = response_lookup_summary.json()

json_response_lookup_summary= json_response_lookup_summary.get("values", {}).get("datas", "")
print(json_response_lookup_summary)

existing_ids = [item['id'] for item in json_response_lookup_summary]
print(existing_ids)
existing_id = random.choice(existing_ids)  # One from existing IDs
less_than_zero = random.randint(-1000, -1) # Less than 0
zero = 0 # 0
greater_than_existing = max(existing_ids) + 1  # Greater than existing
print(greater_than_existing)
large_numbers = random.randint(100000000, 999999999)
delete_ids = [existing_id, less_than_zero, zero, greater_than_existing, large_numbers]

def get_error_message(delete_id):
    if delete_id in existing_ids:
        return "Successful"
    elif delete_id == 0:
        return "Error: Delete ID is zero"
    else:
        return "Error: Invalid Delete ID"

def get_c_response(delete_id):
    return delete_id in existing_ids

data = [{"ID": i+1, "delete_id": delete_id, "c_response": get_c_response(delete_id), "Error message": get_error_message(delete_id)} for i, delete_id in enumerate(delete_ids)]
df = pd.DataFrame(data)

output_csv_path = 'input_delete_lookup.csv'
df.to_csv(output_csv_path, index=False)
print(f"Updated CSV file saved as {output_csv_path}")
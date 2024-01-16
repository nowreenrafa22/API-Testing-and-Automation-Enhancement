import random
import requests
import pandas as pd

login_url = "...login url..."
login_credential = {
    "username": "username",
    "password": "password"
}

get_limit_profile_summary_url="...get-limit-profile url..."
limit_profile_summary_data={
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
headers_limit_profile_summary = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}

response_limit_profile_summary= requests.post(get_limit_profile_summary_url, json=limit_profile_summary_data,
                                headers=headers_limit_profile_summary)
# print(response_lookup_summary)

json_response_limit_profile_summary = response_limit_profile_summary.json()
json_response_limit_profile_summary= json_response_limit_profile_summary.get("values", {}).get("datas", "")
print(json_response_limit_profile_summary)
existing_ids = [item['id'] for item in json_response_limit_profile_summary]
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

data = [{"ID": i+1, "delete_id": delete_id, "c_response": get_c_response(delete_id),
        "Error message": get_error_message(delete_id)} for i, delete_id in enumerate(delete_ids)]
df = pd.DataFrame(data)

output_csv_path = 'delete limit profile\input_delete_limit_profile.csv'
df.to_csv(output_csv_path, index=False)
print(f"Updated CSV file saved as {output_csv_path}")
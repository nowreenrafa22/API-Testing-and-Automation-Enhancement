import itertools
import random
import string
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
# print(json_response_login)
if json_response_login.get("isSuccess") == True:
    access_token = json_response_login.get("data", {}).get("access_token", "")
# print(access_token)
headers_lookup_summary = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}

response_lookup_summary= requests.post(get_lookup_summary_url, json=lookup_summary_data, headers=headers_lookup_summary)
# print(response_lookup_summary)
json_response_lookup_summary = response_lookup_summary.json()
json_response_lookup_summary= json_response_lookup_summary.get("values", {}).get("datas", "")
print(json_response_lookup_summary)
existing_ids = [item['id'] for item in json_response_lookup_summary]

def random_string(length=10):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def create_extended_combinations(update_id):
    fields = ['type', 'code', 'value', 'value_unicode', 'description', 'data_type']
    character = ['varchar', None]
    combinations = list(itertools.product(character, repeat=len(fields)))

    output_df = pd.DataFrame(combinations, columns=fields)
    max_length = 10
    
    for field in fields:
        output_df[field] = output_df[field].apply(lambda x: random_string(random.randint(1, max_length))
                            if x == 'varchar' else x)

    output_df['c_response'] = output_df.apply(lambda row: all(row[field] is not None and (len(row[field]) <= max_length
                            or row[field] == '') for field in ['type', 'code', 'value']), axis=1)

    def error_message(row):
        if row['c_response']:
            return ''
        elif row.get('Error Message'):
            return row['Error Message']

        missing_fields = [field for field in ['type', 'code', 'value'] if row[field] is None]
        # print(missing_fields)
        if missing_fields:
            return 'Required field- {} is missing'.format(' and '.join(missing_fields))
        return 'Unknown Error'

    output_df['Error Message'] = output_df.apply(error_message, axis=1)
    output_df['update_id'] = update_id
    cols = ['update_id', 'c_response', 'Error Message'] + [col for col in output_df.columns 
            if col not in ['update_id', 'c_response', 'Error Message']]
    return output_df[cols]

existing_id = random.choice(existing_ids)  # One from existing IDs
less_than_zero = random.randint(-1000, -1) #less than 0
zero= 0 # 0
greater_than_existing = max(existing_ids) + 1  # Greater than existing
large_numbers = random.randint(100000000, 999999999)
update_ids = [existing_id, less_than_zero, zero, greater_than_existing, large_numbers]

all_dfs = []
for update_id in update_ids:
    temp_df = create_extended_combinations(update_id)
    if update_id not in existing_ids:
        temp_df['c_response'] = False
        temp_df['Error Message'] = 'Invalid id'
    # duplicate_row = temp_df.iloc[-1:].copy()
    # temp_df = pd.concat([temp_df, duplicate_row], ignore_index=True)
    temp_df = pd.concat([temp_df], ignore_index=True)
    all_dfs.append(temp_df)

final_df = pd.concat(all_dfs, ignore_index=True)
final_df['ID'] = range(1, len(final_df) + 1)
columns = ['ID'] + [col for col in final_df.columns if col!='ID']
final_df= final_df[columns]

output_csv_path = 'input_update_lookup.csv'
final_df.to_csv(output_csv_path, index=False)
print(f"Updated CSV file saved as {output_csv_path}")
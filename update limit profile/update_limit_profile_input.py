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

def random_string(length=10):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def random_integer(max_value):
    return random.randint(1, max_value)

def update_limit_profile(update_id, start_id):
    fields = ['name', 'description', 'tps']
    combinations = [(name, desc, tps) 
                    for name in ['varchar', None]
                    for desc in ['varchar', None]
                    for tps in ['integer', None]]
    output_df = pd.DataFrame(combinations, columns=fields)

    for index, row in output_df.iterrows():
        for field in fields:
            if row[field] == 'varchar':
                output_df.at[index, field] = random_string()
            elif row[field] == 'integer':
                output_df.at[index, field] = random_integer(1000)
            else:
                output_df.at[index, field] = None

    output_df['c_response'] = output_df.apply(lambda row: row['name'] is not None and row['tps'] is not None, axis=1)
    output_df['update_id'] = int(update_id)
    # Duplicate rows
    # c_response_true_rows = output_df[output_df['c_response'] == True]
    # duplicate_rows = c_response_true_rows.sample(2).copy()
    # duplicate_rows['c_response'] = False
    # duplicate_rows['row_type'] = 'duplicate'

    # Max length and max length exceed rows
    max_length_row = {
        'name': random_string(50),  # Max length 50
        'description': random_string(100),  # Max length 100
        'tps': str(random_integer(9999)),  # Max length 4 digits
        'c_response': True,
        'row_type': 'max_length',
        'update_id': update_id
    }

    max_length_exceed_row = {
        'name': random_string(51),  # Exceeds max length 50
        'description': random_string(101),  # Exceeds max length 100
        'tps': str(random_integer(10000)),  # Exceeds max length 4 digits
        'c_response': False,
        'row_type': 'max_length_exceed',
        'update_id': update_id
    }

    # Row with non-integer tps value
    non_integer_tps_row = {
        'name': random_string(),
        'description': random_string(),
        'tps': random_string(),  # Non-integer value
        'c_response': False,
        'row_type': 'non_integer_tps',
        'update_id': update_id
    }

    max_length_row_df = pd.DataFrame([max_length_row])
    max_length_exceed_row_df = pd.DataFrame([max_length_exceed_row])
    non_integer_tps_row_df = pd.DataFrame([non_integer_tps_row])

    # Combine all DataFrames
    combined_df = pd.concat([output_df, max_length_row_df, max_length_exceed_row_df, non_integer_tps_row_df], ignore_index=True)

    combined_df['ID'] = range(start_id, start_id + len(combined_df))


    def error_message(row):
        if row['c_response']:
            return ''
        elif 'row_type' in row and row['row_type'] == 'duplicate':
            return 'Duplicate field values'
        elif 'row_type' in row and row['row_type'] == 'max_length_exceed':
            return 'Max length is exceeded'
        elif 'row_type' in row and row['row_type'] == 'non_integer_tps':
            return 'TPS value is not an integer'

        missing_fields = [field for field in ['name', 'tps'] if row[field] is None]
        if missing_fields:
            return 'Required field- {} is missing'.format(' and '.join(missing_fields))
        return 'Unknown Error'

    combined_df['Error Message'] = combined_df.apply(error_message, axis=1)

    cols = ['ID', 'update_id', 'c_response'] + [col for col in combined_df.columns if col not in ['ID', 'update_id', 'c_response']]
    combined_df = combined_df[cols].drop(columns="row_type", errors="ignore")

    return combined_df
# existing_ids = [1, 2, 3, 4]
update_ids = [random.choice(existing_ids), random.randint(-1000, -1), 0, max(existing_ids) + 1, random.randint(100000000, 999999999)]

all_dfs = []
start_id = 1 
for uid in update_ids:
    temp_df = update_limit_profile(uid, start_id)
    start_id += len(temp_df)  # Update start_id for next iteration
    if uid not in existing_ids:
        temp_df['c_response'] = False
        temp_df['Error Message'] = 'Invalid id'
    all_dfs.append(temp_df)

final_df = pd.concat(all_dfs, ignore_index=True)
output_csv_path = 'input_update_limit_profile.csv'
final_df.to_csv(output_csv_path, index=False)
print(f"Updated CSV file saved as {output_csv_path}")
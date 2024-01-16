import pandas as pd
import random
import string

def random_string(length=10):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def random_integer(max_value):
    return random.randint(1, max_value)

def create_limit_profile():
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
    
    # Duplicate rows
    c_response_true_rows = output_df[output_df['c_response'] == True]
    duplicate_rows = c_response_true_rows.sample(2).copy()
    duplicate_rows['c_response'] = False
    duplicate_rows['row_type'] = 'duplicate'

    # Max length and max length exceed rows
    max_length_row = {
        'name': random_string(50),  # Max length 50
        'description': random_string(100),  # Max length 100
        'tps': str(random_integer(9999)),  # Max length 4 digits
        'c_response': True,
        'row_type': 'max_length'
    }

    max_length_exceed_row = {
        'name': random_string(51),  # Exceeds max length 50
        'description': random_string(101),  # Exceeds max length 100
        'tps': str(random_integer(10000)),  # Exceeds max length 4 digits
        'c_response': False,
        'row_type': 'max_length_exceed'
    }

    # Row with non-integer tps value
    non_integer_tps_row = {field: random_string() for field in fields}
    non_integer_tps_row['tps'] = random_string()  # Non-integer value
    non_integer_tps_row['c_response'] = False
    non_integer_tps_row['row_type'] = 'non_integer_tps'

    max_length_row_df = pd.DataFrame([max_length_row])
    max_length_exceed_row_df = pd.DataFrame([max_length_exceed_row])
    non_integer_tps_row_df = pd.DataFrame([non_integer_tps_row])

    # Combine all DataFrames
    combined_df = pd.concat([output_df, duplicate_rows, max_length_row_df, max_length_exceed_row_df, non_integer_tps_row_df], ignore_index=True)

    combined_df['ID'] = range(1, len(combined_df) + 1)

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

    cols = ['ID', 'c_response'] + [col for col in combined_df.columns if col not in ['ID', 'c_response']]
    combined_df = combined_df[cols].drop(columns="row_type", errors="ignore")

    return combined_df

# Generate the modified DataFrame
full_df_modified = create_limit_profile()

# Save to CSV
output_csv_path = 'input_create_limit_profile.csv'
full_df_modified.to_csv(output_csv_path, index=False)
print(f"Updated CSV file saved as {output_csv_path}")
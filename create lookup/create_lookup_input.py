import itertools
import random
import string
import pandas as pd

def random_string(length=10):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def create_extended_combinations():
    fields = ['type', 'code', 'value', 'value_unicode', 'description', 'data_type']
    character = ['varchar', None]

    combinations = list(itertools.product(character, repeat=len(fields)))

    output_df = pd.DataFrame(combinations, columns=fields)
    max_length = 10
    
    for field in fields:
        output_df[field] = output_df[field].apply(lambda x: random_string(random.randint(1, max_length)) if x == 'varchar' else x)

    output_df['c_response'] = output_df.apply(lambda row: all(row[field] is not None and (len(row[field]) <= max_length or row[field] == '') for field in ['type', 'code', 'value']), axis=1)
    
    #duplicate rows
    duplicate_rows = output_df.sample(3).copy()
    duplicate_rows['c_response'] = False
    duplicate_rows['row_type'] = 'duplicate'

    #rows with max_length and max_length_exceed
    max_length_row = {field: random_string(100) for field in fields}
    max_length_row['c_response'] = True
    max_length_row['row_type'] = 'max_length'

    max_length_exceed_row = {field: random_string(random.randint(101, 105)) for field in fields}
    max_length_exceed_row['c_response'] = False
    max_length_exceed_row['row_type'] = 'max_length_exceed'

    max_length_row_df = pd.DataFrame([max_length_row])
    max_length_exceed_row_df = pd.DataFrame([max_length_exceed_row])

    combined_df = pd.concat([output_df, duplicate_rows, max_length_row_df, max_length_exceed_row_df], ignore_index=True)

    combined_df['ID'] = range(1, len(combined_df) + 1)

    def error_message(row):
        if row['c_response']:
            return ''
        elif 'row_type' in row and row['row_type'] == 'duplicate':
            return 'Duplicate field values'
        elif 'row_type' in row and row['row_type'] == 'max_length_exceed':
            return 'Max length is exceeded'

        missing_fields = [field for field in ['type', 'code', 'value'] if row[field] is None]
        if missing_fields:
            return 'Required field- {} is missing'.format(' and '.join(missing_fields))
        return 'Unknown Error'

    combined_df['Error Message'] = combined_df.apply(error_message, axis=1)

    cols = ['ID', 'c_response'] + [col for col in combined_df.columns if col not in ['ID', 'c_response']]
    combined_df = combined_df[cols]
    combined_df= combined_df.drop(columns="row_type", errors="ignore")
    return combined_df

input_csv_df = create_extended_combinations()
input_csv_path = 'input_create_lookup.csv'
input_csv_df.to_csv(input_csv_path, index=False)
print(f"Input CSV file saved as {input_csv_path}")
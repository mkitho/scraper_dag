import json
import pandas as pd
import re
import os
import psycopg2
from datetime import datetime as dt


def connect_database():
    """
    establish connection to postgre database
    """
    connection = psycopg2.connect(user='your-dbusername',
                            password="your-password",
                            host="your-dbhost-ip",
                            database="your-db-name")
    cursor = connection.cursor()
    return connection, cursor


def extract_specs(title: str) -> tuple:
    '''
    extracts machine specifications from listing title
    '''
    # CPU model
    m = re.search(r'i\d', title.lower())
    cpu_model = None if m is None else m.group(0)

    # clockrate
    m = re.search(r'(\d\.\d)\s?(ghz)?', title.lower())
    clockrate =  None if m is None else m.group(1)

    # RAM & storage    
    gb_numbers = re.findall(r'(\d+)\s?gb', title.lower())
    ram = [num for num in gb_numbers if len(num)!=3]
    ram = ram[0] if len(ram) > 0 else None
    storage = [num for num in gb_numbers if len(num)==3]
    storage = storage[0] if len(storage) > 0 else None

    # docking station
    dock = re.search(r'dock', title.lower())
    has_dock = 1 if dock is not None else 0

    # parts only
    parts_in_title = re.search(r'part', title.lower())
    parts_only = 1 if parts_in_title is not None else 0

    # incomplete machine
    missing_parts = re.search(r'no \w+', title.lower())
    has_missing = 1 if missing_parts is not None else 0

    return cpu_model, clockrate, ram, storage, has_dock, parts_only, has_missing



def json_to_structure(jsonfile):
    df = pd.read_json(jsonfile)
    
    # drop duplicates
    df = df.drop_duplicates()

    df['price'] = df.price.fillna('0')
    df['price'] = df.price.apply(lambda x: re.sub(r'[\$,]', '', x))
    df['price'] = df.price.apply(lambda x: re.findall(r'\d+.\d+', x)[0])

    new_columns = df['title'].apply(extract_specs)
    
    df_right = pd.DataFrame.from_records(data=new_columns, columns=['cpu', 'clock', 'ram', 'storage', 'has_dock', 'parts_only', 'has_missing'])
    
    table = pd.concat([df, df_right], axis=1)

    return table


def translate_machine_code(file_name):
    if 'x220' in file_name.lower():
        return '1'
    elif 'x230' in file_name.lower():
        return '2'
    elif 'x240' in file_name.lower():
        return '3'
    else:
        raise NotImplementedError


def insert_records_to_db(connection, cursor, df, machine_code):

    pg_insert_query = \
        """
        INSERT INTO listing (title,stars,condition,price,link,is_auc,cpu,clock,ram,storage,has_dock,parts_only,has_missing,machine_id,date)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
        """
    
    for _, row in df.iterrows():
        row = row.tolist() + [machine_code, dt.today().strftime('%Y-%m-%d')]
        cursor.execute(pg_insert_query, row)

    connection.commit()
    

if __name__=='__main__':
    conn, cur = connect_database()
    
    # read jsons and cleaning
    today_json = os.listdir('./scraped_json')
    today_date = dt.today().strftime('%y%m%d')
    for json_file in [f for f in today_json if today_date in f]:
        # json_file = './scraped_json/thinkpad_x220_200609.json'
        df = json_to_structure(os.path.join('./scraped_json',json_file))
        machine_code = translate_machine_code(json_file)
        insert_records_to_db(conn, cur, df, machine_code)
    
    cur.close()
    conn.close()

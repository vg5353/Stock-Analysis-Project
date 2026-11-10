import os
import yaml
import pandas as pd
import sqlite3

def process_and_save_data():
    dataset_folder = 'data'
    data_rows = []
    
    print(f"1. Searching for YAML files inside the '{dataset_folder}' folder...")
    
    if not os.path.exists(dataset_folder):
        print(f"Error: Folder '{dataset_folder}' not found!")
        return

    # Read the files
    for root, dirs, files in os.walk(dataset_folder):
        for file_name in files:
            if file_name.endswith(('.yaml', '.yml')):
                clean_date = file_name.split('.')[0].split('_')[0]
                file_path = os.path.join(root, file_name)
                
                with open(file_path, 'r') as file:
                    daily_data = yaml.safe_load(file)
                    
                    if isinstance(daily_data, list):
                        for item in daily_data:
                            if isinstance(item, dict):
                                # --- FIX: Remove the old duplicate date columns ---
                                item.pop('Date', None)
                                item.pop('date', None)
                                
                                # Add our clean date
                                item['Parsed_Date'] = pd.to_datetime(clean_date)
                                data_rows.append(item)
                                
    print(f"Found {len(data_rows)} rows of data.")
    
    if len(data_rows) == 0:
        print("ERROR: No data was found.")
        return
        
    print("2. Cleaning data and calculating returns...")
    df = pd.DataFrame(data_rows)
    
    # Make all column names lowercase temporarily
    df.columns = [str(c).lower() for c in df.columns]
    
    # Remove any other accidental duplicate columns
    df = df.loc[:, ~df.columns.duplicated()]
    
    # Safely rename 'ticker' to 'Symbol' and 'parsed_date' to 'Date'
    rename_rules = {}
    if 'ticker' in df.columns:
        rename_rules['ticker'] = 'Symbol'
    if 'parsed_date' in df.columns:
        rename_rules['parsed_date'] = 'Date'
        
    df = df.rename(columns=rename_rules)
    
    if 'Symbol' not in df.columns:
        print("ERROR: Still couldn't find the Ticker/Symbol column.")
        return

    # Drop blank rows and sort
    df = df.dropna(subset=['Symbol', 'close'])
    df = df.sort_values(by=['Symbol', 'Date'])
    
    # Math calculations
    df['Prev_Close'] = df.groupby('Symbol')['close'].shift(1)
    df['Daily_Return'] = (df['close'] - df['Prev_Close']) / df['Prev_Close']
    
    print("3. Saving to SQLite Database...")
    conn = sqlite3.connect('stock_database.db')
    df.to_sql('stock_data', conn, if_exists='replace', index=False)
    conn.close()
    
    print("Success! Database is ready.")

if __name__ == "__main__":
    process_and_save_data()
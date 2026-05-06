import pandas as pd
import os
import glob
import sqlite3

class DataLoader:
    def __init__(self, data_dir='../data'):
        self.data_dir = data_dir
        self.tables = {}
        # Connect to SQLite (creates a file-based database)
        self.conn = sqlite3.connect('insightdb.db', check_same_thread=False)

    def load_data(self, data_dir=None, reset=True):
        """Loads all CSV files from the data directory into Pandas DataFrames and SQLite."""
        if data_dir:
            self.data_dir = data_dir
            
        if not os.path.exists(self.data_dir):
            print(f"Data directory '{self.data_dir}' not found.")
            return self.tables

        csv_files = glob.glob(os.path.join(self.data_dir, "*.csv"))
        
        if not csv_files:
            print(f"No CSV files found in '{self.data_dir}'.")
            return self.tables

        print(f"Found {len(csv_files)} CSV files. Loading into SQLite...")
        
        # Reset tables for new load
        if reset:
            self.tables = {}
            # We could DROP all tables here, but to_sql with if_exists='replace' handles it
        
        for file_path in csv_files:
            try:
                # Extract filename without extension as table name
                table_name = os.path.splitext(os.path.basename(file_path))[0]
                
                # Load CSV
                df = pd.read_csv(file_path)
                
                # Store in dictionary (temporarily kept for backward compatibility with app.py)
                self.tables[table_name] = df
                
                # ------ SQLITE DBMS ADDITION ------
                # Save the table into SQLite database
                df.to_sql(table_name, self.conn, if_exists='replace', index=False)
                # ----------------------------------
                
                print(f"Successfully loaded table: {table_name} into SQLite ({len(df)} rows)")
                
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

        return self.tables

    def get_table(self, table_name):
        return self.tables.get(table_name)

    def get_all_table_names(self):
        return list(self.tables.keys())
    
    def execute_query(self, query, params=None):
        """Helper to execute custom SQL queries on the SQLite database."""
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if query.strip().upper().startswith("SELECT") or query.strip().upper().startswith("PRAGMA"):
            return cursor.fetchall()
        else:
            self.conn.commit()
            return cursor.rowcount

if __name__ == "__main__":
    # Test independantly
    loader = DataLoader(data_dir='./data') # Adjusted path for running directly from backend dir/root if needed
    loader.load_data()

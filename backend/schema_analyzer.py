class SchemaAnalyzer:
    def __init__(self, data_loader):
        """
        :param data_loader: Reference to DataLoader to execute SQL queries.
        """
        self.data_loader = data_loader
        self.schema = {}

    def analyze(self):
        """analyzes all loaded tables and returns a schema dictionary using SQL."""
        tables = self.data_loader.get_all_table_names()
        
        for table_name in tables:
            # Get Row Count via SQL
            res = self.data_loader.execute_query(f"SELECT COUNT(*) FROM \"{table_name}\"")
            row_count = res[0][0] if res else 0

            table_info = {
                "name": table_name,
                "row_count": row_count,
                "columns": [],
                "potential_keys": [],
                "potential_foreign_keys": []
            }

            # Get Schema Info via SQLite PRAGMA
            # Returns: cid, name, type, notnull, dflt_value, pk
            columns_info = self.data_loader.execute_query(f"PRAGMA table_info(\"{table_name}\")")

            for col_row in columns_info:
                col = col_row[1]
                col_type = col_row[2]
                
                # Get Unique Count via SQL
                res_unique = self.data_loader.execute_query(f"SELECT COUNT(DISTINCT \"{col}\") FROM \"{table_name}\"")
                unique_count = res_unique[0][0] if res_unique else 0
                
                # Get Null Count via SQL
                res_null = self.data_loader.execute_query(f"SELECT COUNT(*) FROM \"{table_name}\" WHERE \"{col}\" IS NULL")
                null_count = res_null[0][0] if res_null else 0

                is_numeric = any(t in col_type.upper() for t in ['INT', 'REAL', 'FLOAT', 'NUM'])
                is_datetime = 'date' in col.lower() or 'time' in col.lower() or 'DATETIME' in col_type.upper()
                
                # Context-Aware Classification
                classification = "other"
                if col.endswith("_id") or col == "id":
                    classification = "identifier"
                elif is_datetime:
                    classification = "timestamp"
                elif is_numeric:
                    classification = "numeric"
                elif not is_numeric and unique_count < 50:
                    classification = "categorical"
                
                col_data = {
                    "name": col,
                    "type": col_type,
                    "classification": classification,
                    "unique_count": unique_count,
                    "null_count": null_count
                }
                table_info["columns"].append(col_data)

                # Potential Primary Key Inference
                if classification == "identifier" and unique_count == row_count and null_count == 0 and row_count > 0:
                    table_info["potential_keys"].append(col)

                # Potential Foreign Key Inference
                if classification == "identifier" and not (unique_count == row_count and null_count == 0):
                    # Look for targets
                    potential_targets = []
                    for t in tables:
                        if t == table_name: continue
                        clean_t = t.replace("olist_", "").replace("_dataset", "")
                        clean_col = col.replace("_id", "")
                        if clean_col in clean_t or clean_t in clean_col:
                            potential_targets.append(t)
                    
                    if potential_targets:
                         table_info["potential_foreign_keys"].append({
                             "column": col,
                             "suggested_tables": potential_targets
                         })

            self.schema[table_name] = table_info

        return self.schema

    def get_table_schema(self, table_name):
        return self.schema.get(table_name)


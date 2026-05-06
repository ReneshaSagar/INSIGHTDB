import pandas as pd
import numpy as np

class QualityEngine:
    def __init__(self, data_loader, schemas, validation_policy=None):
        """
        :param data_loader: DataLoader instance with SQLite connection
        :param schemas: Dictionary of {table_name: schema_dict}
        :param validation_policy: AI-generated policy for context-aware auditing
        """
        self.data_loader = data_loader
        self.schemas = schemas
        self.validation_policy = validation_policy or {}
        self.metrics = {}

    def compute_metrics(self):
        """Computes quality metrics and upgraded Trust Score for all tables using SQL queries."""
        
        tables = self.data_loader.get_all_table_names()
        global_max_date = self._get_global_max_date(tables)

        for table_name in tables:
            schema = self.schemas.get(table_name, {})
            table_metrics = {
                "completeness": 0.0,
                "uniqueness": 0.0,
                "freshness": 0.0,
                "orphan_rate": 0.0,
                "outlier_rate": 0.0,
                "negative_rate": 0.0,
                "trust_score": 0.0,
                "issues": [],
                "column_stats": {},
                "sub_scores": {}
            }
            
            res_total = self.data_loader.execute_query(f"SELECT COUNT(*) FROM {table_name}")
            total_rows = res_total[0][0] if res_total else 0
            
            if total_rows == 0:
                self.metrics[table_name] = table_metrics
                continue
                
            cols_info = schema.get("columns", [])
            if not cols_info:
                self.metrics[table_name] = table_metrics
                continue
                
            # 1. Completeness (Weighted 20%)
            total_cells = total_rows * len(cols_info)
            total_nulls = 0
            for col in cols_info:
                res_null = self.data_loader.execute_query(f"SELECT COUNT(*) FROM {table_name} WHERE \"{col['name']}\" IS NULL")
                if res_null: total_nulls += res_null[0][0]
                
            completeness = (total_cells - total_nulls) / total_cells if total_cells > 0 else 0
            table_metrics["completeness"] = round(completeness * 100, 2)
            if completeness < 0.9: table_metrics["issues"].append("High number of missing values")

            # 2. Identifier Health (Weighted 25%)
            id_sub_score = 100
            id_cols = [c for c in cols_info if c["classification"] == "identifier"]
            if id_cols:
                id_nulls = 0
                id_unique_sum = 0
                for c in id_cols:
                    # Using schema info calculated via SQL earlier
                    id_nulls += c["null_count"]
                    id_unique_sum += c["unique_count"]
                
                id_uniqueness_avg = id_unique_sum / (len(id_cols) * total_rows)
                id_sub_score = (id_uniqueness_avg * 80) + ((1 - (id_nulls / (len(id_cols) * total_rows))) * 20)
            
            table_metrics["sub_scores"]["identifier_health"] = round(id_sub_score, 2)

            # 3. FK Integrity / Referential Integrity (Weighted 25%)
            fk_sub_score = 100
            total_orphans = 0
            fks = schema.get("potential_foreign_keys", [])
            if fks:
                for fk in fks:
                    col = fk["column"]
                    target_table_name = fk["suggested_tables"][0]
                    if target_table_name in tables:
                        # Assume PK in target is first potential_key
                        target_pk_list = self.schemas.get(target_table_name, {}).get("potential_keys", [])
                        target_pk = target_pk_list[0] if target_pk_list else None
                        
                        if target_pk:
                            # SQL LEFT JOIN to find orphans
                            q = f"""
                            SELECT COUNT(*) 
                            FROM {table_name} child
                            LEFT JOIN {target_table_name} parent 
                            ON child."{col}" = parent."{target_pk}"
                            WHERE child."{col}" IS NOT NULL AND parent."{target_pk}" IS NULL
                            """
                            res_orphans = self.data_loader.execute_query(q)
                            orphan_count = res_orphans[0][0] if res_orphans else 0
                            
                            if orphan_count > 0:
                                orphan_rate = orphan_count / total_rows
                                total_orphans += orphan_count
                                table_metrics["issues"].append(f"{round(orphan_rate*100, 2)}% orphans in {col} (ref {target_table_name})")
                
                fk_integrity_rate = 1 - (total_orphans / (len(fks) * total_rows))
                fk_sub_score = fk_integrity_rate * 100
            
            table_metrics["orphan_rate"] = round((total_orphans / total_rows) * 100, 2) if total_rows > 0 else 0
            table_metrics["sub_scores"]["fk_integrity"] = round(fk_sub_score, 2)

            # 4. Numeric Sanity (Weighted 15%)
            sanity_sub_score = 100
            total_negatives = 0
            total_outliers = 0
            num_numeric_cols = 0
            
            for col_meta in cols_info:
                col = col_meta["name"]
                if col_meta["classification"] == "numeric":
                    num_numeric_cols += 1
                    
                    # Get AVG and STD using SQLite
                    res_avg = self.data_loader.execute_query(f"SELECT AVG(\"{col}\") FROM {table_name} WHERE \"{col}\" IS NOT NULL")
                    mean = res_avg[0][0] if res_avg and res_avg[0][0] is not None else 0
                    
                    # Calculate variance/std manually since SQLite lacks STDDEV
                    res_var = self.data_loader.execute_query(f"SELECT AVG((\"{col}\" - {mean}) * (\"{col}\" - {mean})) FROM {table_name} WHERE \"{col}\" IS NOT NULL")
                    variance = res_var[0][0] if res_var and res_var[0][0] is not None else 0
                    std = np.sqrt(variance)
                    
                    table_metrics["column_stats"][col] = {"mean": float(mean), "std": float(std)}
                    
                    policy = self.validation_policy.get(table_name, {}).get(col, {})
                    is_unsigned = policy.get("is_unsigned", True)
                    
                    # Check Negatives via SQL
                    res_negs = self.data_loader.execute_query(f"SELECT COUNT(*) FROM {table_name} WHERE \"{col}\" < 0")
                    negs = res_negs[0][0] if res_negs else 0
                    
                    if negs > 0 and is_unsigned:
                        total_negatives += negs
                        table_metrics["issues"].append(f"Negative values in {col} (expected unsigned)")
                    
                    # Range check via SQL
                    p_range = policy.get("range")
                    if p_range and len(p_range) == 2:
                        res_out = self.data_loader.execute_query(f"SELECT COUNT(*) FROM {table_name} WHERE \"{col}\" < {p_range[0]} OR \"{col}\" > {p_range[1]}")
                        out_of_range = res_out[0][0] if res_out else 0
                        if out_of_range > 0:
                            table_metrics["issues"].append(f"Value range violation in {col} (expected {p_range})")
                            total_outliers += out_of_range
                    
                    # Outliers via SQL (Z-score > 3)
                    if std > 0:
                        lower_bound = mean - (3 * std)
                        upper_bound = mean + (3 * std)
                        res_z = self.data_loader.execute_query(f"SELECT COUNT(*) FROM {table_name} WHERE \"{col}\" < {lower_bound} OR \"{col}\" > {upper_bound}")
                        outliers = res_z[0][0] if res_z else 0
                        total_outliers += outliers
                        if outliers / total_rows > 0.05:
                            table_metrics["issues"].append(f"High outlier rate in {col} ({round(outliers/total_rows*100, 1)}%)")

            if num_numeric_cols > 0:
                neg_rate = total_negatives / (num_numeric_cols * total_rows)
                out_rate = total_outliers / (num_numeric_cols * total_rows)
                sanity_sub_score = (1 - neg_rate) * 50 + (1 - out_rate) * 50
            
            table_metrics["negative_rate"] = round((total_negatives / total_rows) * 100, 2) if total_rows > 0 else 0
            table_metrics["outlier_rate"] = round((total_outliers / total_rows) * 100, 2) if total_rows > 0 else 0
            table_metrics["sub_scores"]["numeric_sanity"] = round(sanity_sub_score, 2)

            # 5. Categorical Rare Values via SQL
            for col_meta in cols_info:
                col = col_meta["name"]
                if col_meta["classification"] == "categorical":
                    q = f"""
                    SELECT COUNT(*) FROM (
                        SELECT "{col}", COUNT(*) * 1.0 / {total_rows} as freq 
                        FROM {table_name} 
                        WHERE "{col}" IS NOT NULL 
                        GROUP BY "{col}" 
                        HAVING freq < 0.01
                    )
                    """
                    res_rare = self.data_loader.execute_query(q)
                    rare_count = res_rare[0][0] if res_rare else 0
                    if rare_count > 0:
                        table_metrics["issues"].append(f"{rare_count} rare categories in {col} (<1% frequency)")

            # 6. Freshness (Weighted 15%)
            freshness_score = self._calculate_freshness(table_name, cols_info, global_max_date)
            table_metrics["freshness"] = round(freshness_score, 2)
            table_metrics["sub_scores"]["freshness"] = freshness_score

            # 7. AI Sequence Rules (Contextual Integrity) via SQL
            table_policy = self.validation_policy.get(table_name, {})
            sequence_penalty = 0
            for col, policy in table_policy.items():
                rules = policy.get("sequence_rules", [])
                for rule in rules:
                    before_col = rule.get("before")
                    after_col = rule.get("after")
                    col_names = [c["name"] for c in cols_info]
                    if before_col in col_names and after_col in col_names:
                        # SQLite datetime string comparison
                        q = f"SELECT COUNT(*) FROM {table_name} WHERE \"{before_col}\" > \"{after_col}\" AND \"{before_col}\" IS NOT NULL AND \"{after_col}\" IS NOT NULL"
                        try:
                            res_seq = self.data_loader.execute_query(q)
                            violations = res_seq[0][0] if res_seq else 0
                            if violations > 0:
                                table_metrics["issues"].append(f"Logic Error: {before_col} appears AFTER {after_col} in {violations} rows")
                                sequence_penalty += (violations / total_rows) * 10
                        except: pass
            
            trust_score_deduction = min(sequence_penalty, 20)

            # TRUST SCORE CALCULATION
            trust_score = (
                (id_sub_score * 0.25) +
                (fk_sub_score * 0.25) +
                (completeness * 100 * 0.20) +
                (sanity_sub_score * 0.15) +
                (freshness_score * 0.15)
            )
            table_metrics["trust_score"] = max(0, round(trust_score - trust_score_deduction, 2))
            
            if table_metrics["trust_score"] < 60:
                 table_metrics["issues"].append("Critical: Low overall trust score.")

            self.metrics[table_name] = table_metrics

        return self.metrics

    def _get_global_max_date(self, tables):
        global_max_date = pd.Timestamp.min
        for table_name in tables:
            cols = self.schemas.get(table_name, {}).get("columns", [])
            for c in cols:
                col = c["name"]
                if 'date' in col.lower() or 'time' in col.lower() or c["classification"] == "timestamp":
                    try:
                        res = self.data_loader.execute_query(f"SELECT MAX(\"{col}\") FROM {table_name}")
                        if res and res[0][0]:
                            tm = pd.to_datetime(res[0][0], errors='coerce')
                            if pd.notnull(tm) and tm > global_max_date: 
                                global_max_date = tm
                    except: pass
        return global_max_date if global_max_date != pd.Timestamp.min else pd.Timestamp.now()

    def _calculate_freshness(self, table_name, cols_info, global_max):
        table_max = None
        for c in cols_info:
            col = c["name"]
            if 'date' in col.lower() or 'time' in col.lower() or c["classification"] == "timestamp":
                try:
                    res = self.data_loader.execute_query(f"SELECT MAX(\"{col}\") FROM {table_name}")
                    if res and res[0][0]:
                        tm = pd.to_datetime(res[0][0], errors='coerce')
                        if pd.notnull(tm) and (table_max is None or tm > table_max): 
                            table_max = tm
                except: pass
        
        if not table_max: return 50.0
        days_diff = (global_max - table_max).days
        if days_diff < 30: return 100.0
        if days_diff > 365: return 20.0
        return 100 - (days_diff / 365 * 80)


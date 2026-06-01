import json
from ai_service import AIService

class NormalizationEngine:
    def __init__(self, ai_service=None):
        self.ai_service = ai_service if ai_service else AIService()

    def normalize_text(self, raw_text):
        """Uses Gemini AI to normalize messy, unstructured data into structured CSV format."""
        if not raw_text or not raw_text.strip():
            return "Error: No text provided."

        prompt = f"""
        You are an expert Data Engineer. Analyze the following messy, unstructured, or unnormalised text.
        Your goal is to normalize and structure it into a clean, standardized relational CSV format.
        
        GUIDELINES:
        1. Automatically identify columns and represent the data in uniform CSV rows.
        2. Clean and standardize all header names (use lowercase, clean characters, and underscores, e.g. "customer_name", "order_date", "total_price").
        3. Standardize column values (e.g. format dates as YYYY-MM-DD, clean phone numbers, uniform currency numbers, remove unnecessary spaces).
        4. Keep all business semantics and data rows completely intact.
        5. Output ONLY the raw CSV text. Do NOT include markdown code blocks like ```csv or any conversational text.
        
        MESSY DATA TO STRUCTURE:
        {raw_text}
        """

        clean_csv = self.ai_service._call_gemini_rest(prompt, is_json=False)
        if clean_csv:
            # Strip any residual markdown blocks if Gemini outputs them anyway
            clean_csv = clean_csv.replace("```csv", "").replace("```", "").strip()
            return clean_csv
            
        return "Error: Unable to normalize data using AI core."

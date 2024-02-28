from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import date
load_dotenv()
from analyser import sentimental_analysis, keywords_extractor, summary_extractor, suggession

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
print(url)
print(key)

if not url or not key:
    raise ValueError("Supabase credentials not found in .env file")

supabase = create_client(url, key)
user = '8d34554d-cffe-423f-9ba2-802748df94ed'
date_val = date.today().strftime("%Y-%m-%d")

val_past = supabase.table('logs').select('*').match({'id_name': user}).lte('date_entry', date_val).order('date_entry', desc=True).execute()

print(val_past.data[0].get('date_entry'))
print(date_val)
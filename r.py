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
user = '1489d1f7-d585-45e7-b977-b7ace9fd4645'
date_val = date.today().strftime("%Y-%m-%d")

val = supabase.table('logs').select('*').match({'id_name': user}).lte('date_entry', date_val).execute()
print(val)


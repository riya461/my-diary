from flask import Flask, render_template
import os
from dotenv import load_dotenv
# from supabase import create_client, Client



load_dotenv()
app = Flask(__name__)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
print(url)
print(key)

if not url or not key:
    raise ValueError("Supabase credentials not found in .env file")

# supabase = create_client(url, key)

@app.route('/')
def index():
   
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
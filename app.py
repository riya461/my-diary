from flask import Flask, render_template
import os
from dotenv import load_dotenv
from supabase import create_client, Client



load_dotenv()
app = Flask(__name__)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
print(url)
print(key)

if not url or not key:
    raise ValueError("Supabase credentials not found in .env file")

supabase = create_client(url, key)

@app.route('/')
def index():

 
    response = supabase.table('users_diary').select("*").match({'name': 'Riya'}).execute()
    if response.data:
        name = response.data[0]['name']
        age = response.data[0]['age']
    return render_template('home.html')

@app.route('/page')
def diary_page():
    return render_template('page.html')


if __name__ == '__main__':
    app.run(debug=True)
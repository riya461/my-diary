from flask import Flask, render_template, request, redirect, url_for
import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import date
from analyser import sentimental_analysis, keywords_extractor, summary_extractor, suggession

load_dotenv()
app = Flask(__name__)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
print(url)
print(key)

if not url or not key:
    raise ValueError("Supabase credentials not found in .env file")

supabase = create_client(url, key)



@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == 'POST':
        email: str = request.form['email']
        password: str = request.form['password']
        password2: str = request.form['password2']
        print(email, password, password2)
        if password != password2:
            return render_template('error.html', message="Passwords do not match")
        elif email == "" or password == "":
            return render_template('error.html', message="Please fill out all fields")
        try:
            user = supabase.auth.sign_up({"email": email,"password": password})
        except Exception as e:
            return render_template('error.html', message=str(e))
            
        try:
            user = supabase.auth.sign_in_with_password({"email": email,"password": password})
            return redirect(url_for('about'))

        except Exception as e:
            return render_template('error.html', message=str(e))

    return render_template('signup.html', user="")

# authentication
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
       
        try:
            user = supabase.auth.sign_in_with_password({"email": email,"password": password})

            return redirect(url_for('index'))
        except Exception as e:
            return render_template('error.html', message=str(e))
    return render_template('login.html', user="")

@app.route('/logout')
def logout():
    try:
        supabase.auth.sign_out()
        return redirect(url_for('home'))
    except Exception as e:
        return render_template('error.html', message=str(e))
    

@app.route('/about',methods=["GET", "POST"])
def about():
    if request.method == 'GET':
        user = supabase.auth.get_user()
        user_n = user.json()
        user = str(json.loads(user_n)["user"]["id"])

    if request.method == 'POST':
        user = supabase.auth.get_user()
        user_n = user.json()
        user = str(json.loads(user_n)["user"]["id"])
        name = request.form['name']
        age = request.form['age']
        sex = request.form['sex']
        calm_field = request.form['calm']
        hobby_field = request.form['hobby']
        person_field = request.form['person']
        supabase.table('users_diary').insert([{'name': name,'id': user, 'age': age, 'sex': sex, 'calm_field' : calm_field, 'hobby_field' : hobby_field, 'person_field' : person_field}]).execute()
        return redirect(url_for('index'))
    return render_template('about.html', user= "user")


@app.route('/')
def home():
    return render_template('home.html',user="")
@app.route('/test')
def test():
    return render_template('diary.html',user="")

@app.route('/index')
def index():

    user = supabase.auth.get_user()
    user_n = user.json()
    user = str(json.loads(user_n)["user"]["id"])
    data = supabase.table('users_diary').select('name').match({'id': user}).execute()
    name = data.data[0]['name']

    print(user)
    date_val = date.today().strftime("%Y-%m-%d")
    print(date_val)
    try:
        
        val = supabase.table('logs').select('*').match({'id_name': user, 'date_entry': date_val}).execute()
        print(val.data)
        print(len(val.data))

        # mood tracker for the month 
        month = date.today().strftime("%Y-%m")
        month = month + '-01'
        mood_tracker = supabase.table('logs').select('date_entry','mood').match({'id_name': user}).lte('date_entry', date_val).gte('date_entry', month).order('date_entry',desc=True).execute()
        # past 7 days journal entries
        

        val_past = supabase.table('logs').select('*').match({'id_name': user}).lte('date_entry', date_val).order('date_entry', desc=True).execute()
        if val_past.data[0].get('date_entry') == date_val :
            today = True
        else :
            today = False
        print(val_past.data)
        return render_template('index.html', user=name, today = today, val = val.data, val_past = val_past.data, mood_tracker = mood_tracker.data)
        
    except Exception as e:
        print(e)
        return render_template('error.html', message=str(e))



@app.route('/diary', methods=["GET", "POST"])
def diary():
    user = supabase.auth.get_user()
    user_n = user.json()
    user = str(json.loads(user_n)["user"]["id"])
    data = supabase.table('users_diary').select('name').match({'id': user}).execute()
    name = data.data[0]['name']
    today = date.today().strftime("%Y-%m-%d")
    if request.method == 'POST':
        user = supabase.auth.get_user()
        user_n = user.json()
        user = str(json.loads(user_n)["user"]["id"])
        entry = request.form['entry']
        mood = sentimental_analysis(entry)
        heading = summary_extractor(entry)
        data = supabase.table('users_diary').select('*').match({'id': user}).execute()
        hobby = data.data[0]['hobby_field']
        calm = data.data[0]['calm_field']
        person = data.data[0]['person_field']
        sex = data.data[0]['sex']
        age = data.data[0]['age']
        date_val = date.today().strftime("%Y-%m-%d")


        # code to get suggestion
        try:
            s = suggession(entry,age,sex,person,calm,hobby)
            s1 = s[3]["recommendations"][0:3]
        except:
            return render_template('diary.html', name= name, today = today, prompt = False)

        
        supabase.table('logs').insert([{'id_name': user,'mood': mood,  'content': entry, 'suggestion':s1, 'heading': heading, 'date_entry' : date_val}]).execute()
        
        return render_template('diary.html', name= name, today = today, heading=heading, suggestion = s1,prompt = True)
    return render_template('diary.html', name= name, today = today, prompt = False)



if __name__ == '__main__':
    app.run(debug=True)
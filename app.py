from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests
import random
import os
from datetime import datetime, timedelta
from database import init_db, register_user, check_user, username_exists, nickname_exists, update_user_score, get_leaderboard, get_user_score

app = Flask(__name__)
app.secret_key = 'kunci_rahasia_yang_sangat_aman_12345'

# API Key - ambil dari environment atau gunakan default
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', 'a40ef2dfcac48e883287ffc3c60b9b2c')

QUIZ_QUESTIONS = [
    {
        'question': 'Apa kepanjangan dari AI dalam konteks teknologi?',
        'options': ['Automated Intelligence', 'Artificial Intelligence', 'Advanced Integration', 'Algorithmic Interface'],
        'answer': 1
    },
    {
        'question': 'Library Python mana yang paling populer untuk machine learning?',
        'options': ['NumPy', 'Pandas', 'Scikit-learn', 'Matplotlib'],
        'answer': 2
    },
    {
        'question': 'Apa itu Neural Network dalam AI?',
        'options': ['Database khusus', 'Model komputasi terinspirasi otak manusia', 'Protokol jaringan', 'Bahasa pemrograman'],
        'answer': 1
    },
    {
        'question': 'Apa fungsi utama dari Computer Vision?',
        'options': ['Mengedit video', 'Membuat komputer memahami gambar/video', 'Meningkatkan resolusi layar', 'Mengompres file gambar'],
        'answer': 1
    },
    {
        'question': 'Library Python mana yang digunakan untuk Computer Vision?',
        'options': ['Flask', 'Django', 'OpenCV', 'Beautiful Soup'],
        'answer': 2
    },
    {
        'question': 'Apa kepanjangan dari NLP?',
        'options': ['Natural Language Processing', 'Neural Learning Program', 'Network Layer Protocol', 'New Logic Programming'],
        'answer': 0
    },
    {
        'question': 'Framework deep learning mana yang dikembangkan oleh Google?',
        'options': ['PyTorch', 'Keras', 'TensorFlow', 'Caffe'],
        'answer': 2
    },
    {
        'question': 'Apa itu supervised learning?',
        'options': ['Pembelajaran tanpa data', 'Pembelajaran dengan data berlabel', 'Pembelajaran otomatis', 'Pembelajaran manual'],
        'answer': 1
    },
    {
        'question': 'Teknik apa yang digunakan untuk mengenali wajah dalam gambar?',
        'options': ['Face Detection', 'Image Compression', 'Color Grading', 'Pixel Mapping'],
        'answer': 0
    },
    {
        'question': 'Apa fungsi dari tokenization dalam NLP?',
        'options': ['Membuat password', 'Memecah teks menjadi unit kecil', 'Mengenkripsi data', 'Membuat database'],
        'answer': 1
    },
    {
        'question': 'Model AI apa yang digunakan untuk menghasilkan teks?',
        'options': ['CNN', 'RNN/GPT', 'Decision Tree', 'K-Means'],
        'answer': 1
    },
    {
        'question': 'Apa itu transfer learning dalam AI?',
        'options': ['Memindahkan file', 'Menggunakan model pre-trained untuk tugas baru', 'Transfer data antar server', 'Belajar bahasa baru'],
        'answer': 1
    }
]

init_db()

# ==========================================
# FUNGSI CUACA SIMPLE
# ==========================================
def get_weather_simple(city):
    """
    Fetch cuaca untuk 1 kota dengan data lengkap
    """
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=id"
        resp = requests.get(url, timeout=6)
        data = resp.json()
        
        # Cek status response
        if resp.status_code != 200:
            print(f"❌ Weather API error: {resp.status_code} - {data.get('message', 'Unknown error')}")
            return None
        
        # Emoji cuaca
        weather_icons = {
            'Clear': '☀️',
            'Clouds': '☁️',
            'Rain': '🌧️',
            'Drizzle': '🌦️',
            'Thunderstorm': '⛈️',
            'Snow': '❄️',
            'Mist': '🌫️',
            'Smoke': '🌫️',
            'Haze': '🌫️',
            'Fog': '🌫️'
        }
        
        weather_main = data["weather"][0]["main"]
        weather_icon = weather_icons.get(weather_main, '🌤️')
        
        return {
            "city": data.get("name", city),
            "description": data["weather"][0]["description"].title(),
            "main": weather_main,
            "icon": weather_icon,
            "temp": round(data["main"]["temp"]),
            "feels_like": round(data["main"]["feels_like"]),
            "humidity": data["main"]["humidity"],
            "wind_speed": round(data["wind"]["speed"] * 3.6, 1),
            "pressure": data["main"]["pressure"]
        }
    except Exception as e:
        print(f"❌ Exception in get_weather_simple: {e}")
        return None

# ==========================================
# ROUTES
# ==========================================

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/weather', methods=['POST'])
def weather():
    city = request.form.get('city', '').strip()
    
    if not city:
        return render_template('home.html', weather_simple=None, city=None)
    
    print(f"🌤️ Fetching weather for: {city}")
    weather_info = get_weather_simple(city)
    
    if weather_info:
        print(f"✅ Weather data retrieved for {city}")
    else:
        print(f"❌ Failed to get weather for {city}")
    
    return render_template('home.html', weather_simple=weather_info, city=city)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        nickname = request.form.get('nickname', '').strip()
        
        print(f"\n📝 Registration attempt - Username: {username}, Nickname: {nickname}")
        
        error = None
        
        if not username or not password or not nickname:
            error = 'Semua field harus diisi!'
        elif len(username) < 3:
            error = 'Username minimal 3 karakter!'
        elif len(nickname) < 3:
            error = 'Nickname minimal 3 karakter!'
        elif password != confirm_password:
            error = 'Password tidak cocok!'
        elif len(password) < 6:
            error = 'Password minimal 6 karakter!'
        elif username_exists(username):
            error = 'Username sudah digunakan!'
        elif nickname_exists(nickname):
            error = 'Nickname sudah digunakan!'
        else:
            if register_user(username, password, nickname):
                session['success_message'] = 'Registrasi berhasil! Silakan login.'
                return redirect(url_for('login'))
            else:
                error = 'Registrasi gagal! Coba lagi.'
        
        print(f"❌ Registration failed: {error}")
        return render_template('register.html', error=error)
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        print(f"⚠️ User already logged in: {session.get('nickname')}")
        return redirect(url_for('quiz'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        print(f"\n🔐 Login attempt - Username: {username}")
        
        if not username or not password:
            return render_template('login.html', error='Username dan password harus diisi!')
        
        user = check_user(username, password)
        
        if user:
            session.clear()
            session['user_id'] = user[0]
            session['nickname'] = user[1]
            session['score'] = user[2]
            session.permanent = True
            
            print(f"✅ Login successful - User ID: {user[0]}, Nickname: {user[1]}")
            return redirect(url_for('quiz'))
        else:
            print(f"❌ Login failed for username: {username}")
            return render_template('login.html', error='Username atau password salah!')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    username = session.get('nickname', 'Unknown')
    session.clear()
    print(f"👋 User logged out: {username}")
    return redirect(url_for('home'))

@app.route('/quiz')
def quiz():
    if 'user_id' not in session:
        print("⚠️ Unauthorized access to quiz - redirecting to login")
        return redirect(url_for('login'))
    
    print(f"\n🎯 Quiz accessed by: {session.get('nickname')} (ID: {session.get('user_id')})")
    
    if 'current_question' not in session:
        session['current_question'] = 0
        session['quiz_score'] = 0
        session['asked_questions'] = []
    
    available_questions = [i for i in range(len(QUIZ_QUESTIONS)) if i not in session['asked_questions']]
    
    if not available_questions:
        session['asked_questions'] = []
        available_questions = list(range(len(QUIZ_QUESTIONS)))
    
    question_index = random.choice(available_questions)
    session['asked_questions'].append(question_index)
    session['current_question'] = question_index
    
    question = QUIZ_QUESTIONS[question_index]
    total_score = get_user_score(session['user_id'])
    
    return render_template('quiz.html', 
                         question=question, 
                         question_num=len(session['asked_questions']),
                         total_score=total_score)

@app.route('/check_answer', methods=['POST'])
def check_answer():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    selected = int(request.form.get('answer', -1))
    question_index = session.get('current_question', 0)
    
    correct = QUIZ_QUESTIONS[question_index]['answer']
    is_correct = selected == correct
    
    if is_correct:
        session['quiz_score'] = session.get('quiz_score', 0) + 10
        update_user_score(session['user_id'], 10)
        print(f"✅ Correct answer! User {session['nickname']} +10 points")
    else:
        print(f"❌ Wrong answer by user {session['nickname']}")
    
    return jsonify({
        'correct': is_correct,
        'correct_answer': correct,
        'score': session['quiz_score']
    })

@app.route('/leaderboard')
def leaderboard():
    top_players = get_leaderboard()
    print(f"🏆 Leaderboard accessed - showing {len(top_players)} players")
    return render_template('leaderboard.html', leaderboard=top_players)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 AI Quiz Pro - Starting Application")
    print("="*50)
    print(f"🔑 Weather API Key: {WEATHER_API_KEY[:10]}...")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests
import random
from datetime import datetime, timedelta
from database import init_db, register_user, check_user, username_exists, nickname_exists, update_user_score, get_leaderboard, get_user_score, get_all_users

app = Flask(__name__)
app.secret_key = 'kunci_rahasia_yang_sangat_aman_12345'

WEATHER_API_KEY = '6eb597c47136ab5c3e9d7bc3df3bd7d8'

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

def get_weather_icon(weather_main):
    """Mendapatkan emoji cuaca berdasarkan kondisi"""
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
        'Dust': '🌫️',
        'Fog': '🌫️',
        'Sand': '🌫️',
        'Ash': '🌫️',
        'Squall': '💨',
        'Tornado': '🌪️'
    }
    return weather_icons.get(weather_main, '🌤️')

def translate_weather(weather_desc):
    """Menerjemahkan deskripsi cuaca ke Bahasa Indonesia"""
    translations = {
        'clear sky': 'Cerah',
        'few clouds': 'Sedikit Berawan',
        'scattered clouds': 'Berawan Tersebar',
        'broken clouds': 'Berawan',
        'overcast clouds': 'Mendung',
        'light rain': 'Hujan Ringan',
        'moderate rain': 'Hujan Sedang',
        'heavy intensity rain': 'Hujan Lebat',
        'thunderstorm': 'Badai Petir',
        'snow': 'Salju',
        'mist': 'Kabut',
        'fog': 'Kabut Tebal'
    }
    return translations.get(weather_desc.lower(), weather_desc.title())

def get_weather(city):
    try:
        url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=id'
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            weather_data = []
            
            today = datetime.now().date()
            
            for i in range(3):
                target_date = today + timedelta(days=i)
                
                day_temp = None
                night_temp = None
                day_weather = None
                humidity = None
                wind_speed = None
                pressure = None
                feels_like_day = None
                feels_like_night = None
                
                for item in data['list']:
                    dt = datetime.fromtimestamp(item['dt'])
                    
                    if dt.date() == target_date:
                        hour = dt.hour
                        
                        if 12 <= hour <= 15 and day_temp is None:
                            day_temp = round(item['main']['temp'])
                            feels_like_day = round(item['main']['feels_like'])
                            day_weather = item['weather'][0]
                            humidity = item['main']['humidity']
                            wind_speed = round(item['wind']['speed'] * 3.6, 1)
                            pressure = item['main']['pressure']
                        
                        if 0 <= hour <= 3 and night_temp is None:
                            night_temp = round(item['main']['temp'])
                            feels_like_night = round(item['main']['feels_like'])
                
                if day_temp is None:
                    first_data = data['list'][i*8] if i*8 < len(data['list']) else data['list'][0]
                    day_temp = round(first_data['main']['temp'])
                    feels_like_day = round(first_data['main']['feels_like'])
                    day_weather = first_data['weather'][0]
                    humidity = first_data['main']['humidity']
                    wind_speed = round(first_data['wind']['speed'] * 3.6, 1)
                    pressure = first_data['main']['pressure']
                
                if night_temp is None:
                    night_temp = day_temp - 5
                    feels_like_night = feels_like_day - 5
                
                days_id = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
                day_name = days_id[target_date.weekday()]
                
                uv_index = min(11, max(1, int(day_temp / 5)))
                if day_weather['main'] == 'Clear':
                    uv_index = min(11, uv_index + 2)
                elif day_weather['main'] in ['Clouds', 'Rain']:
                    uv_index = max(1, uv_index - 2)
                
                weather_data.append({
                    'date': target_date.strftime('%d/%m/%Y'),
                    'day': day_name,
                    'day_temp': day_temp,
                    'night_temp': night_temp,
                    'feels_like_day': feels_like_day,
                    'feels_like_night': feels_like_night,
                    'weather_main': day_weather['main'],
                    'weather_desc': translate_weather(day_weather['description']),
                    'weather_icon': get_weather_icon(day_weather['main']),
                    'humidity': humidity,
                    'wind_speed': wind_speed,
                    'pressure': pressure,
                    'uv_index': uv_index
                })
            
            return weather_data
        else:
            return None
    except Exception as e:
        print(f"❌ Error fetching weather: {e}")
        return None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/weather', methods=['POST'])
def weather():
    city = request.form.get('city', 'Jakarta')
    weather_data = get_weather(city)
    return render_template('home.html', weather=weather_data, city=city)

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
            print(f"📊 Session data: {dict(session)}")
            
            return redirect(url_for('quiz'))
        else:
            print(f"❌ Login failed for username: {username}")
            return render_template('login.html', error='Username atau password salah!')
    
    success_msg = session.pop('success_message', None)
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

@app.route('/debug')
def debug():
    """Debug route to see all users"""
    users = get_all_users()
    return f"<pre>{users}</pre>"

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Starting Flask Application")
    print("="*50)
    print("\n📱 Akses dari komputer: http://127.0.0.1:5000")
    print("📱 Akses dari HP (1 WiFi): http://10.135.228.249:5000")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
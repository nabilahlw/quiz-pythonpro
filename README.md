## 🤖 AI Quiz Pro
Web aplikasi quiz interaktif tentang Artificial Intelligence, Machine Learning, Computer Vision, dan Natural Language Processing menggunakan Flask dan SQLite.

#### 🌐 Live Demo
Website: https://nabilahulwana.pythonanywhere.com

#### ✨ Fitur
- Quiz Interaktif - 12 pertanyaan tentang AI, ML, CV, dan NLP
- Sistem User - Register, login, dan profile management
- Leaderboard - Ranking pemain berdasarkan skor
- Widget Cuaca - Data cuaca real-time menggunakan OpenWeatherMap API
- Database - Penyimpanan data user dan skor dengan SQLite
<img src="assets/home.png" width="300">
<img src="assets/login.png" width="300">
<img src="assets/leaderboard.png" width="300">
<img src="assets/quiz.png" width="300">

#### 🛠️ Tools
- Backend: Python 3.10, Flask 3.0.0
- Database: SQLite3
- Frontend: HTML5, CSS3, JavaScript
- API: OpenWeatherMap API
- Deployment: PythonAnywhere

#### 🚀 Instalasi & Menjalankan Lokal
1. Clone Repository
git clone https://github.com/YOUR_USERNAME/ai-quiz-pro.git
cd ai-quiz-pro
2. Buat Virtual Environment
python -m venv .venv
3. Windows
.venv\Scripts\activate
4. Jika Mac/Linux
source .venv/bin/activate
5. Install dependencies
pip install -r requirements.txt
6. Setup database
python database.py
7. Jalankan
python app.py
8. buka browser = http://127.0.0.1:5000

#### 🔑 Konfigurasi API Key
Project ini menggunakan OpenWeatherMap API untuk widget cuaca.
Cara Mendapatkan API Key:
- Daftar di OpenWeatherMap
- Buat API key (gratis)
- Edit kodde file app.py baris 12: WEATHER_API_KEY = 'YOUR_API_KEY_HERE'

#### 📁 Struktur Project
<img src="assets/folders.png" width="300">

#### 🗄️ Database Schema (tabel users)
<img src="assets/db.png" width="300">

####  Credits
1. Flask - Web framework
2. OpenWeatherMap - Weather API
3. PythonAnywhere - Hosting platform

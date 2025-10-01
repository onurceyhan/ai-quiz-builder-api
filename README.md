# AI Quiz Builder API

AI destekli quiz oluşturma ve yönetim API'si. Bu API FastAPI kullanılarak geliştirilmiştir ve frontend Vue.js uygulaması ile entegre çalışacak şekilde tasarlanmıştır.

## Özellikler

- 🔐 JWT tabanlı kimlik doğrulama
- 🌍 Google OAuth entegrasyonu
- 🤖 LangChain + Gemini ile AI destekli quiz oluşturma
- 📝 Quiz CRUD operasyonları
- 🗄️ SQLite/PostgreSQL veritabanı desteği
- 🚀 FastAPI ile yüksek performans
- 📚 Otomatik API dokümantasyonu

## API Endpoints

### Authentication
- `POST /api/auth/register` - Kullanıcı kaydı
- `POST /api/auth/login` - Kullanıcı girişi
- `POST /api/auth/google` - Google OAuth girişi
- `GET /api/auth/me` - Mevcut kullanıcı bilgileri
- `POST /api/auth/logout` - Çıkış yapma

### Quizzes
- `GET /api/quizzes/` - Kullanıcının quizlerini listele
- `POST /api/quizzes/` - Yeni quiz oluştur
- `POST /api/quizzes/generate` - AI ile quiz oluştur
- `GET /api/quizzes/{quiz_id}` - Belirli quiz detayları
- `PUT /api/quizzes/{quiz_id}` - Quiz güncelle
- `DELETE /api/quizzes/{quiz_id}` - Quiz sil

## Kurulum

### 1. Bağımlılıkları Yükleyin

```bash
cd ai-quiz-builder-api
pip install -r requirements.txt
```

### 2. Ortam Değişkenlerini Ayarlayın

`.env` dosyası oluşturun:

```env
# Database Configuration
DATABASE_URL=sqlite:///./ai_quiz_builder.db

# Security Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Gemini AI Configuration (isteğe bağlı)
GEMINI_API_KEY=your-gemini-api-key-here

# Google OAuth Configuration (isteğe bağlı)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Development Settings
DEBUG=True
```

### 3. Veritabanını Başlatın

Uygulama ilk çalıştırıldığında veritabanı tabloları otomatik olarak oluşturulacaktır.

### 4. Sunucuyu Başlatın

```bash
# Geliştirme sunucusu
python start_server.py

# Veya doğrudan uvicorn ile
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API `http://localhost:8000` adresinde çalışacaktır.

## API Dokümantasyonu

Sunucu çalışırken aşağıdaki adreslerden API dokümantasyonuna erişebilirsiniz:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Veri Yapıları

### User (Kullanıcı)
```json
{
  "id": 1,
  "name": "Ahmet Yılmaz",
  "email": "ahmet@example.com",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Quiz
```json
{
  "id": 1,
  "title": "Matematik Temel Kavramlar",
  "prompt": "Lise seviyesinde matematik konularından sorular",
  "category": "Matematik",
  "difficulty": "medium",
  "owner_id": 1,
  "created_at": "2024-01-01T00:00:00Z",
  "questions": [...]
}
```

### Question (Soru)
```json
{
  "id": 1,
  "quiz_id": 1,
  "text": "2x + 5 = 15 denkleminde x'in değeri nedir?",
  "options": ["3", "5", "7", "10"],
  "correct": 1,
  "order": 0,
  "created_at": "2024-01-01T00:00:00Z"
}
```

## Frontend Entegrasyonu

Bu API, `ai-quiz-builder` Vue.js uygulaması ile uyumlu çalışacak şekilde tasarlanmıştır. Frontend'de aşağıdaki değişiklikleri yapmanız gerekebilir:

1. API base URL'ini ayarlayın: `http://localhost:8000/api`
2. Authentication token'ı localStorage'da saklayın
3. HTTP isteklerinde `Authorization: Bearer <token>` header'ını ekleyin

## Geliştirme Notları

- SQLite varsayılan veritabanıdır, production için PostgreSQL kullanın
- Gemini API key olmadan da çalışır (örnek sorular üretir)
- Google OAuth isteğe bağlıdır
- CORS frontend için otomatik ayarlanmıştır
- LangChain frameworkü ile güçlü AI entegrasyonu

## Güvenlik

- JWT token'lar 30 dakika geçerlidir
- Şifreler bcrypt ile hash'lenir
- CORS koruması aktiftir
- SQL injection koruması SQLAlchemy ile sağlanır

## Sorun Giderme

### Veritabanı Sorunları
```bash
# Veritabanını sıfırlamak için
rm ai_quiz_builder.db
# Sunucuyu yeniden başlatın
```

### Bağımlılık Sorunları
```bash
# Virtual environment oluşturun
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. 
# ERP Application

Aplikasi Enterprise Resource Planning (ERP) berbasis Django dengan frontend Tailwind CSS.

## Environment

- Python 3.8+
- Node.js 14+
- Docker Desktop (untuk database dan Redis)

## Setup Project

### 1. Clone Repository

```bash
git clone <repository-url>
cd erp-app
```

### 2. Setup Virtual Environment

```bash
# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Database & Redis

```bash
# Jalankan Docker Compose untuk database dan Redis
docker-compose up -d
```

### 5. Setup Environment Variables

Buat file `.env` di root directory:

```env
PG_DATABASE=postgres
PG_USER=postgres
PG_PASSWORD=postgres
PG_HOST=localhost
PG_PORT=5432
REDIS_PORT=6379
```

### 6. Setup Database

```bash
# Buat migrasi database
python manage.py makemigrations

# Migrasi database
python manage.py migrate

# Seed Command buat generate data dummy   
python manage.py seed_data

# Buat superuser
python manage.py createsuperuser
```

### 7. Install Frontend Dependencies

```bash
npm install
```

### 8. Jalankan Aplikasi

#### Backend (Terminal 1)
```bash
python manage.py runserver
```

#### Frontend (Terminal 2)
```bash
npm run tw
```

### 9. Akses Aplikasi

Buka browser dan akses: 
`http://localhost:8000` dan `http://localhost:8000/admin` untuk admin

## Development Commands

```bash
# Jalankan server development
python manage.py runserver

# Jalankan Tailwind CSS watcher
npm run tw

# Buat migrasi database
python manage.py makemigrations

# Jalankan migrasi
python manage.py migrate

# Seed Command buat generate data dummy   
python manage.py seed_data

# Jalankan test
python manage.py test

# Format code dengan Black
black .

# Sort imports dengan isort
isort .
```


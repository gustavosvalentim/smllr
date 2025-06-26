# smllr

**smllr.io** is a modern, minimal, and powerful URL shortener built with Django. Designed to be fast, elegant, and developer-friendly, it provides core link-shortening features with a sleek dark-mode interface and optional premium features like analytics, branded links, and QR code generation.

## 🚀 Features

- 🔗 Simple and fast link shortening
- 📊 Click analytics and tracking (premium)
- 🧷 Branded short URLs (premium) - TBD
- 🌐 Support for custom domains - TBD
- 📱 QR code generation (premium) - TBD

## 📦 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/gustavosvalentim/smllr.git
cd smllr
```

### 2. Create virtual environment

```bash
uv venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
```

### 3. Install dependencies

```bash
uv sync
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Start the server

```bash
python manage.py runserver
```

### 6. Start postcss (in a different terminal)

```bash
npm run dev
```

Visit http://127.0.0.1:8000 to start shortening URLs!

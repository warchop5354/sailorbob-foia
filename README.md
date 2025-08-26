# SailorBob FOIA Portal

A comprehensive Freedom of Information Act (FOIA) document portal with dark UI, full-text search, and complete deployment infrastructure.

## Features

- **Dark, sleek UI** with fast performance
- **Full-text search** across PDFs, DOC, DOCX with OCR support
- **Document uploads** with automatic text extraction
- **Admin controls** and analytics dashboard
- **Mobile app** (iOS Expo React Native)
- **Role-based authentication** (admin/mod/user)
- **VPS primary storage** with shared host backups
- **Production-ready** infrastructure configs

## Stack

- **Backend**: Python Django + DRF, PostgreSQL, Meilisearch, Celery, Redis
- **Frontend**: React + Tailwind CSS (dark theme), Next.js
- **Mobile**: Expo React Native (iOS)
- **Search**: Meilisearch with facets, ranking, highlights
- **Storage**: Local VPS filesystem with nightly backups to shared host
- **OCR**: Tesseract for scanned PDFs
- **Infrastructure**: Docker, Nginx, systemd, rclone

## Quick Start

### Development

```bash
# Clone and setup
git clone <repo-url>
cd sailorbob-foia

# Copy environment files
cp .env.example .env
cp backend/.env.example backend/.env
cp web/.env.example web/.env
cp mobile/.env.example mobile/.env

# Start development services
docker-compose up -d

# Setup backend
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Setup frontend
cd ../web
npm install
npm run dev

# Setup mobile
cd ../mobile
npm install
npx expo start
```

### Production

See [docs/DEPLOY.md](docs/DEPLOY.md) for complete production deployment instructions.

## Documentation

- [Setup Guide](docs/SETUP.md) - Development and production setup
- [Deployment Guide](docs/DEPLOY.md) - Infrastructure and deployment
- [API Documentation](docs/API.md) - REST API reference
- [Operations Manual](docs/OPS.md) - Maintenance and operations

## Domain Setup

- **Public hostname**: `foia.sailorbob.com` → VPS (Nginx → web + api)
- **API endpoint**: `https://foia.sailorbob.com/api/`
- **Admin panel**: `https://foia.sailorbob.com/admin/`

## Architecture

```
foia-portal/
├── backend/          # Django + DRF API server
├── web/              # React frontend (Next.js + Tailwind)
├── mobile/           # Expo React Native iOS app
├── infra/            # Docker, Nginx, systemd configs
├── scripts/          # Utilities and maintenance scripts
└── docs/             # Documentation
```

## License

MIT License - see [LICENSE](LICENSE) file for details.
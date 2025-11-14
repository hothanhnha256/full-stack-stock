# Stock Report Backend (Flask)

Backend API cho ứng dụng quản lý báo cáo chứng khoán.

## Features

- ✅ RESTful API endpoints (JSON)
- ✅ CRUD mã chứng khoán
- ✅ Tự động gửi email báo cáo (4 PM Mon-Fri)
- ✅ Web scraping FireAnt.vn với Playwright
- ✅ PostgreSQL database
- ✅ SendGrid email integration

## Tech Stack

- Flask + SQLAlchemy
- PostgreSQL (Aiven)
- Playwright (headless browser)
- APScheduler (scheduled tasks)
- SendGrid (email)

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium

# Setup environment
cp .env.example .env
# Edit .env with your credentials

# Run Flask server
python run.py
```

Server runs on http://localhost:5000

## API Endpoints

- `GET /api/symbols` - Lấy danh sách mã
- `POST /api/symbols` - Thêm mã mới
- `DELETE /api/symbols/<id>` - Xóa mã
- `POST /api/report/send` - Gửi báo cáo ngay

## Deploy to Render.com

1. Connect GitHub repo
2. Select `stock-report-fullstack/backend`
3. Set environment variables from `.env.example`
4. Deploy!

Render.yaml đã được cấu hình sẵn.

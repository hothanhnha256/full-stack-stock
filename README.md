# 📊 Stock Report Fullstack App

Ứng dụng quản lý danh sách mã chứng khoán và tự động gửi báo cáo qua email.

## 🎯 Features

- ✅ **Dashboard UI đẹp** với Next.js + Tailwind CSS
- ✅ **CRUD mã chứng khoán** (thêm/xóa)
- ✅ **Gửi báo cáo tức thì** hoặc **tự động 4 PM** (Thứ 2-6)
- ✅ **Web scraping** FireAnt.vn với Playwright
- ✅ **Email báo cáo** qua SendGrid
- ✅ **PostgreSQL** database
- ✅ **Dark mode** support

## 🏗️ Architecture

```
Frontend (Next.js)          Backend (Flask)
   Vercel              ←→      Render.com
     ↓                            ↓
React Query                  PostgreSQL (Aiven)
  Axios                      Playwright + SendGrid
```

## 📁 Project Structure

```
stock-report-fullstack/
├── frontend/          # Next.js app
│   ├── src/
│   │   ├── app/       # Pages & providers
│   │   └── lib/       # API client
│   └── package.json
│
└── backend/           # Flask API
    ├── app/           # Controllers, models, tasks
    ├── migrations/    # Database migrations
    ├── run.py         # Flask entry point
    └── requirements.txt
```

## 🚀 Local Development

### Backend (Flask)

```bash
cd backend
pip install -r requirements.txt
playwright install chromium

# Setup .env
cp .env.example .env
# Edit .env với credentials

python run.py
# → http://localhost:5000
```

### Frontend (Next.js)

```bash
cd frontend
npm install

# .env.local đã có
npm run dev
# → http://localhost:3000
```

## 🌐 Deployment

### Backend → Render.com

1. Push code lên GitHub
2. Render Dashboard → New Web Service
3. Connect repo: `stock-report-fullstack`
4. Root directory: `backend`
5. Build command: `pip install -r requirements.txt && playwright install --with-deps chromium`
6. Start command: `python run.py`
7. Add environment variables:
   - `DATABASE_URL` (PostgreSQL URL)
   - `SENDGRID_API_KEY`
   - `SENDER_EMAIL`
   - `RECIPIENT_EMAIL`
   - `ENABLE_SCHEDULER=1`
8. Deploy!

### Frontend → Vercel

1. Vercel Dashboard → Import Project
2. Select `stock-report-fullstack` repo
3. Framework: Next.js
4. Root directory: `frontend`
5. Environment variable:
   - `NEXT_PUBLIC_API_URL=https://your-backend.onrender.com`
6. Deploy!

## 📧 Email Report Sample

```
📊 BÁO CÁO THỊ TRƯỜNG CHỨNG KHOÁN

📈 Tổng quan thị trường:
VN-Index: +1.23%
HNX-Index: +0.89%

📌 Danh sách mã theo dõi (14 mã):
DLG: Giá 20.812,27 tỷ | P/E 12.5 | ROE 15.2%
...
```

## 🛠️ Tech Stack

**Frontend:**

- Next.js 16 + React 19
- TanStack React Query
- Tailwind CSS 4
- Axios

**Backend:**

- Flask + SQLAlchemy
- PostgreSQL
- Playwright (web scraping)
- APScheduler
- SendGrid

## 📝 API Endpoints

- `GET /api/symbols` - Danh sách mã
- `POST /api/symbols` - Thêm mã (body: `{code: "VNM"}`)
- `DELETE /api/symbols/<id>` - Xóa mã
- `POST /api/report/send` - Gửi báo cáo ngay

## 👨‍💻 Author

**hothanhnha256**

## 📄 License

MIT

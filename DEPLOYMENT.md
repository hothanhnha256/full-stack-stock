# 🚀 Hướng Dẫn Deploy Production

## Bước 1️⃣: Deploy Backend lên Render.com

### 1.1. Tạo Web Service mới

1. Truy cập [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub repo: `hothanhnha256/StockMVC`
4. Chọn branch: `main`

### 1.2. Cấu hình Build Settings

```
Name: stock-report-backend
Region: Singapore (hoặc gần Việt Nam nhất)
Branch: main
Root Directory: backend
Runtime: Python 3
Build Command: pip install -r requirements.txt && playwright install --with-deps chromium
Start Command: gunicorn --bind 0.0.0.0:$PORT run:app
```

### 1.3. Environment Variables (quan trọng!)

Thêm các biến môi trường sau:

```bash
DATABASE_URL=<your-aiven-postgresql-url>
# Ví dụ: postgresql://user:password@host:port/database?sslmode=require

SENDGRID_API_KEY=<your-sendgrid-api-key>
SENDER_EMAIL=<email-gui-di>
RECIPIENT_EMAIL=<email-nhan>

FLASK_ENV=production
ENABLE_SCHEDULER=1
SECRET_KEY=<random-secret-key>
```

**Lưu ý**: Copy DATABASE_URL từ file `.env` hiện tại của bạn!

### 1.4. Deploy

- Click **"Create Web Service"**
- Đợi ~5-10 phút để build
- Sau khi deploy xong, copy URL (ví dụ: `https://stock-report-backend.onrender.com`)

### 1.5. Test Backend API

```bash
curl https://stock-report-backend.onrender.com/api/symbols
```

Phải trả về JSON array `[]` hoặc danh sách mã.

---

## Bước 2️⃣: Deploy Frontend lên Vercel

### 2.1. Import Project

1. Truy cập [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Import GitHub repo: `hothanhnha256/StockMVC`

### 2.2. Cấu hình Build Settings

```
Project Name: stock-report-frontend
Framework Preset: Next.js
Root Directory: frontend
Build Command: npm run build
Output Directory: .next
Install Command: npm install
```

### 2.3. Environment Variables

Thêm biến môi trường:

```bash
NEXT_PUBLIC_API_URL=https://stock-report-backend.onrender.com
```

**⚠️ QUAN TRỌNG**: Thay `stock-report-backend.onrender.com` bằng URL thực tế của backend Render!

### 2.4. Deploy

- Click **"Deploy"**
- Đợi ~2-3 phút
- Vercel sẽ tự động deploy và tạo URL (ví dụ: `https://stock-report-frontend.vercel.app`)

---

## Bước 3️⃣: Kiểm Tra Hoạt Động

### 3.1. Test Frontend

1. Mở URL Vercel: `https://your-app.vercel.app`
2. Dashboard phải hiển thị đẹp
3. Danh sách mã phải load được (hoặc empty nếu chưa có)

### 3.2. Test CRUD

- **Thêm mã**: Nhập "VNM" → Click "Thêm mã"
- **Xóa mã**: Click nút "Xóa" → Confirm
- Kiểm tra mã có thêm/xóa trong database không

### 3.3. Test Gửi Báo Cáo

- Click **"📧 Gửi báo cáo ngay"**
- Đợi 30-60 giây
- Check email `RECIPIENT_EMAIL` phải nhận được báo cáo

### 3.4. Test Scheduler (Tự động 4 PM)

- Đợi đến 4 PM (thứ 2-6)
- Email tự động gửi
- Hoặc check logs Render: `https://dashboard.render.com/web/your-service/logs`

---

## 🔧 Troubleshooting

### Lỗi Backend: "Application failed to respond"

```bash
# Check logs Render:
https://dashboard.render.com/web/your-service/logs

# Thường do:
- DATABASE_URL sai format
- Thiếu environment variables
- Build command sai
```

### Lỗi Frontend: "Failed to fetch"

```bash
# Kiểm tra:
1. NEXT_PUBLIC_API_URL đúng chưa?
2. Backend có CORS enabled không?
3. Backend URL có accessible không?

# Test:
curl https://your-backend.onrender.com/api/symbols
```

### Lỗi Email không gửi

```bash
# Kiểm tra:
1. SENDGRID_API_KEY valid?
2. SENDER_EMAIL verified in SendGrid?
3. Check logs Render có lỗi không?
```

---

## 📊 Monitoring

### Backend Logs (Render)

```
https://dashboard.render.com/web/stock-report-backend/logs
```

### Frontend Logs (Vercel)

```
https://vercel.com/your-team/stock-report-frontend/logs
```

---

## 🔄 Update Code Sau Này

### Update Backend

```bash
git add backend/
git commit -m "Update backend: [mô tả]"
git push origin main
```

→ Render tự động deploy trong ~5 phút

### Update Frontend

```bash
git add frontend/
git commit -m "Update frontend: [mô tả]"
git push origin main
```

→ Vercel tự động deploy trong ~2 phút

---

## 💡 Tips

1. **Free Tier Render**: Backend sẽ sleep sau 15 phút không dùng → request đầu tiên chậm ~30s
2. **Vercel Free**: Unlimited bandwidth, 100GB/month
3. **Database Aiven**: Free tier có giới hạn 25MB
4. **SendGrid Free**: 100 emails/day

---

## 📞 Support

Nếu gặp vấn đề:

1. Check logs Render/Vercel
2. Test API endpoints bằng curl
3. Kiểm tra environment variables
4. Đọc lại README.md

**Good luck! 🚀**

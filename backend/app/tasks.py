import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
from vnstock import Vnstock
from .models import StockSymbol
import pandas as pd
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from python_http_client.exceptions import HTTPError
import json
import re
import time
from playwright.sync_api import sync_playwright

def get_total_value_from_fireant(symbol: str) -> str:
    """
    Lấy tổng giá trị giao dịch từ FireAnt bằng Playwright.
    Scrape trực tiếp text "Tổng giá trị" từ DOM.
    """
    try:
        url = f"https://fireant.vn/ma-chung-khoan/{symbol}"
        print(f"🔗 Đang mở FireAnt: {url}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_load_state("networkidle", timeout=20000)
            time.sleep(2)
            
            raw = None
            try:
                # Tìm element chứa text "Tổng giá trị" và "tỷ"
                cand = page.locator("css=div:has-text('Tổng giá trị') span:has-text('tỷ')")
                cand.first.wait_for(state="visible", timeout=5000)
                raw = cand.first.inner_text(timeout=2000).strip()
            except Exception as e:
                print(f"⚠️ Không tìm thấy element với locator: {e}")
            
            # Fallback: Tìm trong HTML
            if not raw:
                html = page.content()
                m = re.search(r"Tổng giá trị[\s\S]{0,200}?([\d,\.]+)\s*tỷ", html, re.IGNORECASE)
                if m:
                    raw = m.group(1).strip() + " tỷ"
            
            browser.close()
            
            if not raw:
                print(f"⚠️ Không tìm thấy 'Tổng giá trị' cho {symbol}")
                return "N/A"
            
            # Parse số từ raw text - giữ nguyên format từ FireAnt
            # FireAnt dùng dấu chấm cho hàng nghìn và dấu phẩy cho thập phân
            value_str = raw.replace("tỷ", "").strip()
            
            if value_str:
                print(f"✅ FireAnt - {symbol}: Tổng giá trị = {value_str} tỷ")
                return f"{value_str} tỷ"
            
            return "N/A"
            
    except Exception as e:
        print(f"❌ Lỗi Playwright: {e}")
        import traceback
        traceback.print_exc()
        return "N/A"


def index_change_str(stock, symbol: str, today_query: str) -> str:
    """
    Tính tăng/giảm chỉ số theo chuẩn:
    delta = close_today - close_prev_session
    Lùi 10 ngày để luôn có >= 2 phiên (tránh cuối tuần/nghỉ lễ).
    """
    start_dt = (datetime.datetime.now() - datetime.timedelta(days=10)).strftime("%Y-%m-%d")
    df = stock.quote.history(symbol=symbol, start=start_dt, end=today_query, interval='1D')

    if df is None or len(df) < 2:
        return f"Không có đủ dữ liệu {symbol}."

    last2 = df.tail(2)
    prev_close = float(last2.iloc[0]['close'])
    today_row  = last2.iloc[1]
    close = float(today_row['close'])
    volume = float(today_row.get('volume', 0)) / 1e6

    delta = close - prev_close
    s = f"{close:,.2f} điểm - "
    if delta > 0:
        s += f" tăng {delta:,.2f} điểm"
    elif delta < 0:
        s += f" giảm {abs(delta):,.2f} điểm"
    else:
        s += " không thay đổi"
    
    # Lấy tổng giá trị từ FireAnt
    total_value_fireant = get_total_value_from_fireant(symbol)
    s += f" - Tổng giá trị giao dịch: {total_value_fireant}"
    s += f" - Tổng khối lượng giao dịch: {volume:,.1f} triệu cổ phiếu"
    return s


def send_report():
    app = current_app._get_current_object()
    cfg = app.config
    # Vnstock v3.3.0 yêu cầu symbol, dùng symbol mặc định để khởi tạo
    stock = Vnstock().stock(symbol='VNM', source='VCI')

    print("🔔 Chuẩn bị gửi báo cáo...")
    syms = StockSymbol.query.all()
    codes = [s.code for s in syms]
    print(f"🔔 Chuẩn bị gửi báo cáo cho {len(codes)} mã: {codes}")
    print(f"ENV SENDGRID_API_KEY present: {bool(cfg.get('SENDGRID_API_KEY'))}")
    print(f"ENV FROM_EMAIL: {cfg.get('EMAIL_USER')}")
    if not codes:
        print("Không có mã nào để gửi báo cáo.")
        app.logger.info("Không có mã nào để gửi báo cáo.")
        return

    today_query = datetime.datetime.now().strftime("%Y-%m-%d")
    today_vn = datetime.datetime.now().strftime("%d/%m/%Y")

    # Lấy dữ liệu chỉ số VN-Index
    try:
        vnindex_str = index_change_str(stock, 'VNINDEX', today_query)
    except Exception as e:
        app.logger.warning(f"Lỗi lấy VN-Index: {e}")
        vnindex_str = "Không có dữ liệu VN-Index hôm nay."

    try:
        hnxindex_str = index_change_str(stock, 'HNXINDEX', today_query)
    except Exception as e:
        app.logger.warning(f"Lỗi lấy HNX-Index: {e}")
        hnxindex_str = "Không có dữ liệu HNX-Index hôm nay."

    try:
        df = stock.trading.price_board(codes)
    except Exception as e:
        app.logger.error(f"Lỗi lấy bảng giá: {e}")
        return

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join([str(i) for i in col if i]) for col in df.columns.values]

    df['price_change'] = df.get('match_match_price', 0) - df.get('match_reference_price', 0)

    def format_change(val):
        try:
            val = float(val)
        except:
            return "không xác định"
        if val > 0:
            return f"tăng {val:,.0f} đ"
        elif val < 0:
            return f"giảm {abs(val):,.0f} đ"
        else:
            return "không thay đổi"

    lines = []
    lines.append(f"BÁO CÁO THỊ TRƯỜNG NGÀY {today_vn}\n")
    lines.append("KÍNH GỬI: CHỦ TỊCH HĐQT TẬP ĐOÀN ĐỨC LONG GIA LAI\n")
    lines.append(f"Chỉ số VN-Index: {vnindex_str}\n")
    lines.append(f"Chỉ số HNX-Index: {hnxindex_str}\n")

    for i, (_, row) in enumerate(df.iterrows(), start=1):
        code = row.get('listing_symbol') or row.get('symbol') or ""
        close = row.get('match_match_price', 0)
        change = format_change(row.get('price_change', 0))
        vol = row.get('match_accumulated_volume', 0)
        try:
            vol = int(vol)
        except:
            pass
        name = row.get('listing_organ_name', '')
        lines.append(f"{i}. {code} ({name})")
        lines.append(f"   Giá đóng cửa: {close:,.0f} đ - {change}")
        lines.append(f"   Tổng khối lượng giao dịch: {vol:,}\n")


    report_text = "\n".join(lines)
    print(report_text)
    app.logger.info("Đã tạo xong nội dung báo cáo."+report_text)
    # Thông tin email
    sender = cfg['EMAIL_USER']
    recipient = cfg.get('REPORT_RECIPIENT_EMAIL') or sender
    password = cfg['EMAIL_PASSWORD']
    host = cfg['EMAIL_HOST']
    port = cfg['EMAIL_PORT']
    sendgrid_api = cfg.get('SENDGRID_API_KEY')

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = f"📊 BÁO CÁO THỊ TRƯỜNG NGÀY {today_vn}"
    msg.attach(MIMEText(report_text, "plain"))

    if sendgrid_api:
        print("Gửi email qua SendGrid...")
        app.logger.info("Gửi email qua SendGrid...")
        try:
            status = send_email_via_sendgrid(msg['Subject'], report_text, sender, recipient, sendgrid_api)
            if status == 202:
                print("✅ Đã gửi báo cáo thành công qua SendGrid.")
                app.logger.info("✅ Đã gửi báo cáo thành công qua SendGrid.")
            else:
                print(f"❌ Lỗi gửi email qua SendGrid, mã trạng thái: {status}")
                app.logger.error(f"❌ Lỗi gửi email qua SendGrid, mã trạng thái: {status}")
        except Exception as e:
            print(f"❌ Lỗi gửi email qua SendGrid: {e}")
            app.logger.error(f"❌ Lỗi gửi email qua SendGrid: {e}")
        return
    try:
        with smtplib.SMTP_SSL(host, port) as server:
            server.login(sender, password)
            server.sendmail(sender, [recipient], msg.as_string())
        print("✅ Đã gửi báo cáo thành công.")
        app.logger.info("✅ Đã gửi báo cáo thành công.")
    except Exception as e:
        print(f"❌ Lỗi gửi email: {e}")
        app.logger.error(f"❌ Lỗi gửi email: {e}")


def send_email_via_sendgrid(subject, content, sender, recipient,api):
    message = Mail(from_email=sender, to_emails=recipient, subject=subject, plain_text_content=content)
    try:
        sg = SendGridAPIClient(api)
        resp = sg.send(message)
        return resp.status_code  # 202 = OK
    except HTTPError as e:
        # Trả về body lỗi (thường là 400/401/403: sender chưa verify, API key sai,…)
        print(f"SendGrid HTTPError: {e.status_code} - {e.body}")
        raise RuntimeError(f"SendGrid error: {getattr(e, 'body', e)}")
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from .models import db, StockSymbol
from .tasks import send_report
import threading
from vnstock import Vnstock
from .models import ListedSymbol

global_app = None

def set_global_app(app):
    global global_app
    global_app = app

bp = Blueprint('main', __name__, template_folder='templates')

# ==================== JSON API ENDPOINTS ====================
@bp.route('/api/symbols', methods=['GET'])
def api_get_symbols():
    """Get all stock symbols"""
    symbols = StockSymbol.query.order_by(StockSymbol.created_at).all()
    return jsonify([{
        'id': s.id,
        'code': s.code,
        'created_at': s.created_at.isoformat()
    } for s in symbols])

@bp.route('/api/symbols', methods=['POST'])
def api_add_symbol():
    """Add new stock symbol"""
    data = request.get_json()
    code = data.get('code', '').strip().upper()
    
    if not code:
        return jsonify({'error': 'Code is required'}), 400
    
    exists = StockSymbol.query.filter_by(code=code).first()
    if exists:
        return jsonify({'error': f'Symbol {code} already exists'}), 400
    
    symbol = StockSymbol(code=code)
    db.session.add(symbol)
    db.session.commit()
    
    return jsonify({
        'id': symbol.id,
        'code': symbol.code,
        'created_at': symbol.created_at.isoformat(),
        'message': f'Added {code} successfully'
    }), 201

@bp.route('/api/symbols/<int:symbol_id>', methods=['DELETE'])
def api_delete_symbol(symbol_id):
    """Delete a stock symbol"""
    symbol = StockSymbol.query.get(symbol_id)
    if not symbol:
        return jsonify({'error': 'Symbol not found'}), 404
    
    code = symbol.code
    db.session.delete(symbol)
    db.session.commit()
    
    return jsonify({'message': f'Deleted {code} successfully'}), 200

@bp.route('/api/report/send', methods=['POST'])
def api_send_report():
    """Trigger manual report sending"""
    threading.Thread(target=send_report_in_context).start()
    return jsonify({'message': 'Report generation started. Check your email in 1-2 minutes.'}), 202

# ==================== WEB UI ROUTES (Keep existing) ====================
@bp.route('/', methods=['GET', 'POST'])
def index():
    # Xử lý POST:
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            code = request.form.get('code', '').strip().upper()
            if not code:
                flash("Vui lòng nhập mã chứng khoán", "warning")
            else:
                exists = StockSymbol.query.filter_by(code=code).first()
                if exists:
                    flash(f"Mã {code} đã tồn tại", "danger")
                else:
                    s = StockSymbol(code=code)
                    db.session.add(s)
                    db.session.commit()
                    flash(f"Đã thêm mã {code}", "success")
            return redirect(url_for('main.index'))
        elif action == 'delete':
            sym_id = request.form.get('symbol_id')
            s = StockSymbol.query.get(sym_id)
            if s:
                db.session.delete(s)
                db.session.commit()
                flash(f"Đã xóa mã {s.code}", "info")
            else:
                flash("Không tìm thấy mã để xóa", "danger")
            return redirect(url_for('main.index'))
        elif action == 'send':
            threading.Thread(target=send_report_in_context).start()
            flash("Đã kích hoạt gửi báo cáo. Vui lòng kiểm tra email.", "info")
            return redirect(url_for('main.index'))
    # GET: hiển thị
    symbols = StockSymbol.query.order_by(StockSymbol.created_at).all()
    auto_info = "Mỗi ngày lúc 16:00 (Asia/Ho_Chi_Minh)"
    return render_template('index.html', symbols=symbols, auto_info=auto_info)

def send_report_in_context():
    with global_app.app_context():  # ✅ Tạo context đúng cách
        send_report()


@bp.route('/api/search-symbols')
def search_symbols():
    query = request.args.get('q', '').upper()
    matched = ListedSymbol.query.filter(ListedSymbol.symbol.contains(query)).limit(10).all()
    result = [{'symbol': s.symbol, 'organName': s.organ_name} for s in matched]
    return jsonify(result)

@bp.route('/debug/send')
def debug_send():
    with global_app.app_context():
        send_report()
    return "Triggered send_report()", 200

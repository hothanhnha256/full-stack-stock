from flask_sqlalchemy import SQLAlchemy
import uuid
from datetime import datetime

db = SQLAlchemy()

def generate_uuid():
    return str(uuid.uuid4())

class StockSymbol(db.Model):
    __tablename__ = "stock_symbols"
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    code = db.Column(db.String(20), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ListedSymbol(db.Model):
    __tablename__ = "listed_symbols"
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    symbol = db.Column(db.String(10), nullable=False, unique=True, index=True)
    organ_name = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

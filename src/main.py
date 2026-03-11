import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from src.models import db
from src.config import Config

# Import route blueprints
from src.routes.auth import auth_bp
from src.routes.books import books_bp
from src.routes.members import members_bp
from src.routes.borrowings import borrowings_bp
from src.routes.fines import fines_bp
from src.routes.reports import reports_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config.from_object(Config)

# Initialize extensions
CORS(app)
jwt = JWTManager(app)
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(books_bp, url_prefix='/api/books')
app.register_blueprint(members_bp, url_prefix='/api/members')
app.register_blueprint(borrowings_bp, url_prefix='/api/borrowings')
app.register_blueprint(fines_bp, url_prefix='/api/fines')
app.register_blueprint(reports_bp, url_prefix='/api/reports')

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.route('/api/health')
def health_check():
    return {'status': 'healthy', 'message': 'Library Management System API is running'}

if __name__ == '__main__':
    app.run(
        host='0.0.0.0', 
        port=5000, 
        debug=True
    )

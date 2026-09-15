from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'rahasia-gameportal-2026'

    # === REGISTER SEMUA BLUEPRINT ===
    from app.routers.auth import auth_bp
    from app.routers.admin import admin_bp
    from app.routers.web import web_bp
    from app.routers.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)

    return app
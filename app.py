from flask import Flask
from models import db
from flask_login import LoginManager
from config import Config
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Создаем папку для загрузок если не существует
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager = LoginManager(app)
    from models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    login_manager.login_view = 'auth.login'

    with app.app_context():
        from models import User
        db.create_all()

        if not User.query.filter_by(email='admin@example.com').first():
            from werkzeug.security import generate_password_hash
            admin = User(username='admin', email='admin@example.com',
                         password_hash=generate_password_hash('admin'), is_admin=True)
            db.session.add(admin)
            db.session.commit()

    from auth import auth_bp
    from shop import shop_bp
    from admin import admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(admin_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
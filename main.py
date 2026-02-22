from flask import Flask, redirect, url_for
from config.settings import Config
from routes.api_routes import api_bp
from routes.admin_routes import admin_bp
from routes.auth_routes import auth_bp

app = Flask(__name__, static_folder='statics')
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def index():
    return redirect(url_for('admin.dashboard'))

@app.errorhandler(401)
def unauthorized(e):
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)

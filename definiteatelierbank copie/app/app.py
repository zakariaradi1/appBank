import os
from flask import Flask, render_template
from controllers.user_controller import user_bp  
from controllers.admin_controller import admin_bp
from errors.error_handler import register_error_handlers  
import secrets

app = Flask(__name__, template_folder="templates", static_folder="static")

# Enregistrement des Blueprints
app.register_blueprint(user_bp, url_prefix='/user') 
app.register_blueprint(admin_bp, url_prefix='/admin')  

# Gestion des erreurs
register_error_handlers(app)

# Clé secrète
app.secret_key = secrets.token_hex(32)

# Récupérer le port défini par Render (ou utiliser 5000 en local)
PORT = int(os.environ.get('PORT', 5000))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=PORT)

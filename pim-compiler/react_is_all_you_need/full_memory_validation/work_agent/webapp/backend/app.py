from flask import Flask
from routes import create_app
from config import Config

def create_flask_app():
    app = create_app()
    return app

if __name__ == '__main__':
    app = create_flask_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
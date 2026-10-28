"""
WSGI Entry Point for Cloud Deployment (Render, PythonAnywhere, Railway, Heroku)
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()

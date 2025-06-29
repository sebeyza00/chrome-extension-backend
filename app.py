# Simple app.py entry point for Railway deployment
# This imports our production backend

from production_backend import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)

# run.py
import os
from app import create_app

app = create_app(os.getenv("FLASK_ENV", "development"))

if __name__ == "__main__":
    flask_env = os.getenv("FLASK_ENV", "development")
    if flask_env == "development":
        print("Khởi chạy Flask development server tại http://127.0.0.1:5000 (debug=True)...")
        app.run(host="127.0.0.1", port=5000, debug=True)
    else:
        try:
            from waitress import serve
            print("Khởi chạy máy chủ Waitress WSGI tại http://127.0.0.1:5000...")
            serve(app, host="127.0.0.1", port=5000)
        except ImportError:
            app.run(host="127.0.0.1", port=5000)

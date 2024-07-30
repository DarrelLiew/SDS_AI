from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    host = '0.0.0.0' if os.environ.get('PORT') else '127.0.0.1'
    port = int(os.environ.get('PORT', 3002))  # Default to 3002 for local, override to 8080 in container
    print(f"Running Flask app on http://localhost:{port}")
    app.run(debug=True, host=host, port=port)
    
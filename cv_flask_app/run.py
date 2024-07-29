from app import create_app

app = create_app()

if __name__ == '__main__':
    port = 3002
    print(f"Running Flask app on http://localhost:{port}")
    app.run(debug=True, port=port)
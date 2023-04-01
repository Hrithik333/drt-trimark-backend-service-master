from app import app


if __name__ == "__main__":
    app.run(threaded=True, host='0.0.0.0', port=1125, use_reloader=False)

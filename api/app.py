import os
from flask import Flask
from dotenv import load_dotenv


load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

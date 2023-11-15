# To run flask api command -> flask run

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'
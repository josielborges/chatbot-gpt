import os

from dotenv import load_dotenv
from flask import Flask, render_template
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = 'gpt-4'

app = Flask(__name__)
app.config.from_pyfile('config.py')


@app.route('/')
def home():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)

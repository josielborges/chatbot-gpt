import os
from time import sleep

from dotenv import load_dotenv
from flask import Flask, render_template, request
from openai import OpenAI

from assistant import create_assistant, create_thread

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = 'gpt-4'

app = Flask(__name__)
app.config.from_pyfile('config.py')

assistant = create_assistant()
thread = create_thread()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/chat', methods=["POST"])
def chat():
    prompt = request.json['msg']
    response = bot(prompt)
    response_text = response.content[0].text.value
    return response_text


def bot(prompt):
    max_try = 1
    i = 0

    while True:
        try:
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role='user',
                content=prompt
            )

            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant.id
            )

            while run.status != 'completed':
                run = client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )

            history = list(client.beta.threads.messages.list(thread_id=thread.id).data)
            response = history[0]
            return response
        except Exception as e:
            i += 1
            if i > max_try:
                return "Erro no GPT: %s" % e
            print('Erro de comunicação com OpenAI:', e)
            sleep(1)


if __name__ == '__main__':
    app.run(debug=True)

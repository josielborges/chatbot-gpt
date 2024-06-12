import json
import os
import uuid
from time import sleep

from dotenv import load_dotenv
from flask import Flask, render_template, request
from openai import OpenAI

from assistant import get_json
from persona_selection import personas, select_persona
from tools import functions
from vision import analyse_image

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = 'gpt-4-1106-preview'

app = Flask(__name__)
app.config.from_pyfile('config.py')

assistant = get_json()
thread_id = assistant['thread_id']
vector_store_id = assistant['vector_store_id']
assistant_id = assistant['assistant_id']

STATUS_COMPLETED = 'completed'
STATUS_REQUIRES_ACTION = 'requires_action'

sent_image_path = None
UPLOAD_FOLDER = 'data'


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/chat', methods=["POST"])
def chat():
    prompt = request.json['msg']
    response = bot(prompt)
    response_text = response.content[0].text.value
    return response_text


@app.route('/image_upload', methods=["POST"])
def image_upload():
    global sent_image_path
    print(request.files)
    if 'imagem' in request.files:
        image = request.files['imagem']

        filename = str(uuid.uuid4()) + os.path.splitext(image.filename)[1]
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        image.save(filepath)
        sent_image_path = filepath

        print(image)
        return 'Imagem recebida com sucesso', 200
    return 'Nenhum arquivo foi enviado', 400


def bot(prompt):
    global sent_image_path
    max_try = 1
    i = 0

    while True:
        try:
            persona = personas[select_persona(prompt)]

            vision_response = ''
            if sent_image_path != None:
                vision_response = analyse_image(sent_image_path)
                vision_response += '. Na resposta final, apresente detalhes da descrição da imagem.'
                os.remove(sent_image_path)
                sent_image_path = None

            client.beta.threads.messages.create(
                thread_id=thread_id,
                role='user',
                content=vision_response + '\n' + prompt
            )

            client.beta.threads.messages.create(
                thread_id=thread_id,
                role='user',
                content=f"""
                Assuma, de agora em diante, a personalidade abaixo. 
                Ignore as personalidades anteriores.

                # Persona
                {persona}
                """
                # file_ids=file_ids
            )

            client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=prompt
                # file_ids=file_ids
            )

            run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id
            )

            while run.status != STATUS_COMPLETED:
                run = client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )

                print(f"Status: {run.status}")

                if run.status == STATUS_REQUIRES_ACTION:
                    called_tools = run.required_action.submit_tool_outputs.tool_calls
                    called_actions_responses = []

                    for called_tool in called_tools:
                        function_name = called_tool.function.name
                        chosen_function = functions[function_name]
                        arguments = json.loads(called_tool.function.arguments)
                        print(arguments)
                        function_response = chosen_function(arguments)

                        called_actions_responses.append(
                            {
                                'tool_call_id': called_tool.id,
                                'output': function_response
                            }
                        )

                    run = client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread_id,
                        run_id=run.id,
                        tool_outputs=called_actions_responses
                    )

            history = list(client.beta.threads.messages.list(thread_id=thread_id).data)
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

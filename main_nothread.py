import os
from time import sleep

from dotenv import load_dotenv
from flask import Flask, render_template, request
from openai import OpenAI

from document_selection import select_document, select_context
from persona_selection import select_persona, personas

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = 'gpt-4'

app = Flask(__name__)
app.config.from_pyfile('config.py')


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/chat', methods=["POST"])
def chat():
    prompt = request.json['msg']
    response = bot(prompt)
    response_text = response.choices[0].message.content
    return response_text


def bot(prompt):
    max_try = 1
    i = 0

    persona = personas[select_persona(prompt)]
    context = select_context(prompt)
    selected_document = select_document(context)

    while True:
        try:
            system_prompt = f"""
            Você é um chatbot de atendimento a clientes de um e-commerce. 
            Você não deve responder perguntas que não sejam dados do e-commerce informado!
            
            Você deve gerar respostas utilizando o contexto abaixo.
            Você deve adotar a persona abaixo.
            
            # Contexto
            {selected_document}
            
            # Persona
            {persona}
            """

            print(system_prompt)

            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=1,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                model=model
            )
            return response
        except Exception as e:
            i += 1
            if i > max_try:
                return "Erro no GPT: %s" % e
            print('Erro de comunicação com OpenAI:', e)
            sleep(1)


if __name__ == '__main__':
    app.run(debug=True)

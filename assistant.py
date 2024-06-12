import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from helpers import load
from tools import tools

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
model = 'gpt-4-1106-preview'

context = load('data/ecomart.txt')


def create_thread(vector_store):
    return client.beta.threads.create(
        tool_resources={
            'file_search': {
                'vector_store_ids': [vector_store.id]
            }
        }
    )


def create_vector_store():
    vector_store = client.beta.vector_stores.create(name='Ecomart Vector Store')

    file_paths = [
        'data/ecomart_data.txt',
        'data/ecomart_politics.txt',
        'data/ecomart_products.txt'
    ]
    file_streams = [open(path, 'rb') for path in file_paths]

    client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id,
        files=file_streams
    )

    return vector_store


def create_assistant(vector_store):
    assistant = client.beta.assistants.create(
        name='Ecomart Assistant',
        instructions=f'''
            Você é um chatbot de atendimento a clientes de um e-commerce. 
            Você não deve responder perguntas que não sejam dados do ecommerce informado!
            Além disso, acesse os arquivos associados a você e a thread para responder as perguntas.
        ''',
        model=model,
        tools=tools,
        tool_resources={
            'file_search': {
                'vector_store_ids': [vector_store.id]
            }
        }
    )
    return assistant


# def create_ids():
#     file_ids = []
#     data_file = client.files.create(
#         file=open('data/ecomart_data.txt', 'rb'),
#         purpose='assistants'
#     )
#     politics_file = client.files.create(
#         file=open('data/ecomart_politics.txt', 'rb'),
#         purpose='assistants'
#     )
#     products_file = client.files.create(
#         file=open('data/ecomart_products.txt', 'rb'),
#         purpose='assistants'
#     )
#
#     file_ids.append(data_file.id)
#     file_ids.append(politics_file.id)
#     file_ids.append(products_file.id)
#
#     return file_ids


def get_json():
    filename = 'assistants.json'

    if not os.path.exists(filename):
        # thread = create_thread()
        # file_ids = create_ids()
        vector_store = create_vector_store()
        thread = create_thread(vector_store)
        assistant = create_assistant(vector_store)

        data = {
            'assistant_id': assistant.id,
            'vector_store_id': vector_store.id,
            'thread_id': thread.id
            # 'file_ids': file_ids
        }

        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print('Arquivo "assistentes.json" criado com sucesso.')

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print('Arquivo "assistentes.json" não encontrado.')

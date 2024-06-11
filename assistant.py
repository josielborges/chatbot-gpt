import os

from dotenv import load_dotenv
from openai import OpenAI

from helpers import load
from persona_selection import personas

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = 'gpt-4'

context = load('data/ecomart.txt')


def create_thread():
    return client.beta.threads.create()


def create_assistant():
    assistant = client.beta.assistants.create(
        name='Ecomart Assistant',
        instructions=f"""
            Você é um chatbot de atendimento a clientes de um e-commerce. 
            Você não deve responder perguntas que não sejam dados do ecommerce informado!
            Além disso, adote a persona abaixo para responder ao cliente.
            
            ## Contexto
            {context}
            
            ## Persona
            
            {personas["neutro"]}
        """,
        model=model,
    )
    return assistant

import os

from dotenv import load_dotenv
from openai import OpenAI

from helpers import *

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = 'gpt-4'

ecomart_data = load('data/ecomart_data.txt')
ecomart_pproduct = load('data/ecomart_products.txt')
ecomart_politics = load('data/ecomart_politics.txt')


def select_document(openai_response):
    if 'políticas' in openai_response:
        return ecomart_data + "\n" + ecomart_politics
    elif "produtos" in openai_response:
        return ecomart_data + "\n" + ecomart_pproduct
    else:
        return ecomart_data


def select_context(user_prompt):
    system_prompt = f"""
    A empresa EcoMart possui três documentos principais que detalham diferentes aspectos do negócio:

    #Documento 1 "\n {ecomart_data} "\n"
    #Documento 2 "\n" {ecomart_pproduct} "\n"
    #Documento 3 "\n" {ecomart_politics} "\n"

    Avalie o prompt do usuário e retorne o documento mais indicado para ser usado no contexto da resposta. Retorne dados se for o Documento 1, políticas se for o Documento 2 e produtos se for o Documento 3. 

    """

    respose = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=1
    )

    return respose.choices[0].message.content.lower()

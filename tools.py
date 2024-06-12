import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
model = 'gpt-4-1106-preview'

tools = [
    {
        'type': 'file_search'
    }
]

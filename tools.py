import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
model = 'gpt-4-1106-preview'

tools = [
    {
        'type': 'file_search'
    },
    # See more at https://cursos.alura.com.br/course/python-gpt-crie-chatbot-com-ia/task/148376
    {
        'type': 'function',
        'function': {
            'name': 'validate_promo_code',
            'description': 'Valide um código promocional com base nas diretrizes de Descontos e Promoções da empresa',
            'parameters': {
                'type': 'object',
                'properties': {
                    'code': {
                        'type': 'string',
                        'description': 'O código promocional, no formato, CUPOM_XX. Por exemplo: CUPOM_ECO',
                    },
                    'expiration_date': {
                        'type': 'string',
                        'description': f'A validade do cupom, caso seja válido e esteja associado as políticas. '
                                       f'No formato DD/MM/YYYY.',
                    },
                },
                'required': ['code', 'expiration_date'],
            }
        }
    }
]


def validate_promo_code(arguments):
    print('Entrou na função')
    code = arguments.get('code')
    expiration_date = arguments.get('expiration_date')

    return f'''
        
        # Formato de Resposta
        
        {code} com validade: {expiration_date}. 
        Ainda, diga se é válido ou não para o usuário.
        '''


functions = {
    'validate_promo_code': validate_promo_code
}

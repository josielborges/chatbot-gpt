def load(filename):
    try:
        with open(filename, 'r') as file:
            data = file.read()
            return data
    except IOError as e:
        print(f'Erro ao carregar o arquivo: {e}')


def save(filename, data):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(data)
    except IOError as e:
        print(f'Erro ao salvar o arquivo: {e}')

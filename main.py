import sys
import os
import json
from modules.server import Server
from modules.telegram_bot import Bot


def is_number(s):
    try:
        int(s)
    except:
        return False
    return True

def make_variable(variable_name, variable_value, is_string):
    if is_string:
        variable_value = f"'{variable_value}'"
    return f'{variable_name} = {variable_value}\n'

def input_value(text, is_numeric, default=None):
    value = ''
    if default != None:
        text = f'{text} (значение по умолчанию {default})'
    text += ':'
    while not value or is_number(value) != is_numeric:
        print(text)
        value = input()

        if default != None and not value:
            value = default
            break
    
    if is_number(value):
        return int(value)
    return value

def make_config(file_path, data):
    with open(file_path, 'w') as f:
        f.write(json.dumps(data))

def read_config(file_path):
    with open(file_path, 'r') as f:
        return json.loads(f.read())

if __name__ == '__main__':
    try:
        BASE_PATH = sys._MEIPASS
    except Exception:
        BASE_PATH = os.path.abspath(".")

    FILENAME = 'config.json'
    FILE_PATH = os.path.join(BASE_PATH, FILENAME)
    print(FILE_PATH)

    should_skip = False
    if not os.path.isfile(FILE_PATH):
        data = { 
            'token': input_value('Введите токен вашего бота', False),
            'chat': input_value('Введите чат с вашим ботом', True, 0)
            }
        make_config(FILE_PATH, data)
        should_skip = True

    config = read_config(FILE_PATH)
    if not should_skip and (not config['token'] or not config['chat']):
        config = { 
            'token': input_value('Введите токен вашего бота', False, config['token']),
            'chat': input_value('Введите чат с вашим ботом', True, config['chat'])
            }
        make_config(FILE_PATH, config)

    server = Server('localhost', 12345, Bot, config)
    server.run()

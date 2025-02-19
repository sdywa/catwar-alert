import sys
import os
import signal
import json
from modules.server import Server, ServerType
from modules.transmitter import Transmitter
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
    return f"{variable_name} = {variable_value}\n"


def input_value(text, is_numeric, default=None):
    valid_func = lambda x: True
    if is_numeric:
        valid_func = lambda x: is_number(x) == is_numeric

    value = ""
    if default is not None:
        text = f'{text} (значение по умолчанию: "{default}")'
    text += ":"
    while not value or not valid_func(value):
        print(text)
        value = input()

        if default is not None and not value:
            value = default
            break

    if is_number(value):
        return int(value)
    return value


def make_config(file_path, data):
    with open(file_path, "w") as f:
        f.write(json.dumps(data))


def read_config(file_path):
    with open(file_path, "r") as f:
        return json.loads(f.read())


def generate_config(file_path):
    inputs = {
        "token": {
            "text": "Введите токен вашего бота",
            "is_numeric": False
        },
        "chat": {
            "text": "Введите ID чата с ботом",
            "is_numeric": True,
            "default": 0
        },
        "server": {
            "text": "Введите адрес удалённого сервера",
            "is_numeric": False
        },
    }
    questions = {
        "d": [ "token", "chat" ],
        "t": [ "server", "chat" ],
        "s": [ "token" ]
    }

    if not os.path.isfile(file_path):
        data = {
            "type": input_value(
                "Введите тип использования (d - обычное, t - передатчик, s - сервер для передатчика)", False, "d"
            )
        }

        for question in questions[data["type"]]:
            data[question] = input_value(**inputs[question])

        make_config(file_path, data)
        return data

    config = read_config(file_path)
    if any(not config[question] for question in questions[config["type"]]):
        for question in questions[config["type"]]:
            input_info = inputs[question]
            input_info["default"] = config[question]
            config[question] = input_value(**input_info)
    
        make_config(file_path, config)

    return config


if __name__ == "__main__":
    try:
        BASE_PATH = sys._MEIPASS
    except Exception:
        BASE_PATH = os.path.abspath(".")

    FILENAME = "config.json"
    FILE_PATH = os.path.join(BASE_PATH, FILENAME)
    config = generate_config(FILE_PATH)

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    type = config.pop("type")
    if type == "t":
        server = Transmitter("localhost", 20360, config)
        server.run()
    else:
        server = Server(
            ServerType.DEFAULT if type == "d" else ServerType.MULTI_USER, 
            "localhost", 
            20360, 
            Bot, 
            config,
        )
        server.run()

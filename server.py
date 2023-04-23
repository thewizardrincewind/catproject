from flask import Flask, request, jsonify
import logging
import resourses
import random as r

app = Flask(__name__)


logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():

    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    return jsonify(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        res['response']['text'] = 'Привет! Хочешь получить смешное фото кота?'
        res['response']['buttons'] = get_suggests(user_id)
        return

    if req['request']['original_utterance'].lower() in [
        'ладно',
        'конечно',
        'да',
        'хорошо'
    ]:
        # Пользователь согласился, прощаемся.
        res['response']['card'] = {}
        res['response']['card']['image_id'] = r.choice(resourses.imgs)
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['title'] = '<speaker audio="alice-sounds-animals-cat-3.opus"> Держи! Хотите ещё картинку?'

    res['response']['text'] = \
        f"Ну хорошо"
    with open('users.txt', 'rw') as file:
        file.write(req['session']['user_id'] + ': ' + c)
    return


def get_suggests(user_id):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    suggests.append({
        "title": "Ладно",
        "url": "https://market.yandex.ru/search?text=слон",
        "hide": True
    })

    return suggests


if __name__ == '__main__':
    app.run()

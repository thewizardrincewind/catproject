from flask import Flask, request, jsonify, make_response
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

  
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)
  
  
def handle_dialog(req, res):
    global c
    user_id = req['session']['user_id']
    if req['session']['new']:
        sessionStorage[user_id] = {'count': 0, 'first_name': None}
        res['response']['text'] = 'Привет! Назови свое имя!'
        req['session']['new'] = False
        return
    if sessionStorage[user_id]['first_name'] is None:
        # в последнем его сообщение ищем имя.
        first_name = get_first_name(req)
        sessionStorage[user_id]['first_name'] = first_name
        if first_name is None:
            res['response']['text'] = \
                'Не расслышала имя. Повтори, пожалуйста!'
        # если нашли, то приветствуем пользователя.
        # И спрашиваем какой город он хочет увидеть.
        else:
          name = sessionStorage[user_id]['first_name']
          res['response']['text'] = f'Приятно познакомиться, {name}! Хочешь получить смешное фото кота?'
          res['response']['buttons'] = [{'title': 'Да!'}, {'title': 'Нет.'}]
          return
        
    else:
      if req['request']['original_utterance'].lower() in [
          'ладно',
          'конечно',
          'да!',
          'да',
          'хорошо'
      ]:
          res['response']['card'] = {}
          res['response']["tts"] = "<speaker audio=\"dialogs-upload/f81fc424-3b56-450c-92a4-c2d12f946ce4/b637d9f1-db29-4323-b6ad-a3d1d98b613e.opus\">"
          res['response']['buttons'] = [{'title': 'Да!'}, {'title': 'Нет.'}]
          res['response']['card']['image_id'] = r.choice(resourses.imgs)
          res['response']['card']['type'] = 'BigImage'
          sessionStorage[user_id]['count'] += 1
          res['response']['card']['title'] = 'Держи! Хочешь ещё картинку?'
      res['response']['text'] = \
          f"Ну хорошо!"
      with open('users.txt', 'w+') as f:
        f.write(sessionStorage[user_id]['first_name'] + ': ' + str(sessionStorage[user_id]['count']) + '\n')
      return
        
def get_first_name(req):
  # перебираем сущности
  for entity in req['request']['nlu']['entities']:
      # находим сущность с типом 'YANDEX.FIO'
      if entity['type'] == 'YANDEX.FIO':
          # Если есть сущность с ключом 'first_name',
          # то возвращаем ее значение.
          # Во всех остальных случаях возвращаем None.
          return entity['value'].get('first_name', None)


if __name__ == '__main__':
    app.run()

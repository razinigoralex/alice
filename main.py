from flask import Flask, request
import logging
import os


class App:
    def __init__(self, namespace):
        self.app = Flask(namespace)
        self.sessionStorage = {}
        self.agrees = ['ладно', 'куплю', 'покупаю', 'хорошо']

        self.build()

    def build(self):
        @self.app.route("/post", methods=["POST"])
        def main():
            content = request.get_json(force=True)

            logging.info(f"Request: {content!r}")

            response = {
                "session": content["session"],
                "version": content["version"],
                "response": {
                    "end_session": False
                }
            }

            response = self.handle_dialog(content, response)

            logging.info(f"Response: {response!r}")

            return response

    def handle_dialog(self, req, resp):
        user_id = req["session"]["user_id"]

        if req["session"]["new"]:
            self.sessionStorage[user_id] = {
                'suggests': [
                    "Не хочу.",
                    "Не буду.",
                    "Отстань!",
                ]
            }

            resp["response"]["text"] = "Привет! Купи слона!"
            resp['response']['buttons'] = self.get_suggests(user_id)
            return resp

        for agree in self.agrees:
            if agree in req["request"]["original_utterance"].lower():
                resp['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
                resp['response']['end_session'] = True
                return resp

        resp['response']['text'] = \
            f"Все говорят '{req['request']['original_utterance']}', а ты купи слона!"
        resp['response']['buttons'] = self.get_suggests(user_id)

        return resp

    def get_suggests(self, user_id):
        session = self.sessionStorage[user_id]

        suggests = [
            {'title': suggest, 'hide': True} for suggest in session['suggests'][:2]
        ]

        session["suggests"] = session["suggests"][1:]
        self.sessionStorage[user_id] = session

        if len(suggests) < 2:
            suggests.append({
                "title": "Ладно",
                "url": "https://market.yandex.ru/search?text=слон",
                "hide": True
            })

        return suggests

    def get_app(self):
        return self.app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        filename="alice.txt",
                        format="%(asctime)s %(levelname)s %(name)s %(message)s")

    app = App(__name__).get_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

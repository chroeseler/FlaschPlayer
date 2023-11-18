import threading

from flask import Flask, render_template, request

import text_queue as txt

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        print(request.form['text'])
        txt.put(request.form['text'])
        return render_template('wait.html', text=request.form['text'], length=5 + len(request.form['text']))
    return render_template('landing.html')


@app.route('/wait/')
def waiting():
    return render_template('landing.html')


def main() -> None:
    txt.setup()
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
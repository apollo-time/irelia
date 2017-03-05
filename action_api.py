from env.korean_chess import KoreanChess
from flask import Flask
from flask import request
import json
import sqlite3
import operator
import random


app = Flask(__name__, static_url_path='/home/irelia/public_html')


@app.route('/play')
def play():
    return app.send_static_file('web/play.html')


@app.route("/action")
def action():
    state_map = request.args.get('state_map')

    side = request.args.get('side')
    if not state_map or side not in ('b', 'r'):
        return json.dumps({'error': True, 'msg': 'invalid params', 'data': {'state_map': state_map, 'side': side}})

    state_map = json.loads(state_map)

    if side == 'b':
        reverse_state_map = KoreanChess.reverse_state_map(state_map)
        db_name = './q_blue.db'
    else:
        db_name = './q_red.db'

    state_key = KoreanChess.convert_state_key(reverse_state_map)

    conn = sqlite3.connect(db_name)

    c = conn.cursor()

    c.execute("SELECT quality_json FROM t_quality WHERE state_key='" + state_key + "'")

    result = c.fetchone()
    actions = KoreanChess.get_actions(KoreanChess.reverse_state_map(state_map), side)
    if result:
        q_values = json.loads(result)
        max_action = max(q_values.iteritems(), key=operator.itemgetter(1))[0]
        if max_action not in actions:
            action = random.choice(actions)
            return error('There is no the action! ' + max_action)
        else:
            action = actions[max_action]
    else:
        action = random.choice(actions)

    c.close()
    return json.dumps(action)

    # return "Hello World!"


@app.route("/actions")
def actions():
    state_map = request.args.get('state_map')
    side = request.args.get('side')
    if not state_map or side not in ('b', 'r'):
        return json.dumps({'error': True, 'msg': 'invalid params', 'data': {'state_map': state_map, 'side': side}})
    result = KoreanChess.get_actions(json.loads(state_map), side)

    return json.dumps(result)


def error(msg, data = None):
    return json.dumps({'error':True,'msg':msg,'data':data})


if __name__ == "__main__":
    app.run()

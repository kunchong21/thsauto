import functools

import flask
from flask import Flask, request, jsonify, render_template, json
from thsauto import ThsAuto
import time
import sys
import threading
import realHq

import os

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

auto = ThsAuto()

client_path = None
def run_client():
    os.system('start ' + client_path)
    

lock = threading.Lock()
next_time = 0
interval = 0.5
def interval_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global interval
        global lock
        global next_time
        lock.acquire()
        now = time.time()
        print(request.url)
        print(request.values)
        token = request.values.get("token")
        if token is not None and token == "xsk":
            print(token)
        else:
            rt = ({'code': 1, 'status': 'failed', 'msg': '{}'.format("个人测试使用")}, 400)
            lock.release()
            return rt

        if now < next_time:
            time.sleep(next_time - now)
        try:
            rt = func(*args, **kwargs)
        except Exception as e:
            rt = ({'code': 1, 'status': 'failed', 'msg': '{}'.format(e)}, 400)
        next_time = time.time() + interval
        lock.release()
        return rt
    return wrapper

@app.route('/thsauto/trader')
@interval_call
def trader():
    #return 'Hello World! %s'%name
    return render_template('trade.html')

def callback(result):
    callback = request.args.get('callback', None)
    print(result)
    if callback is not None:
        return callback + "(" + json.dumps(result) + ")"
    else:
        return jsonify(result), 200

@app.route('/thsauto/balance', methods = ['GET'])
@interval_call
def get_balance():
    auto.active_mian_window()
    result = auto.get_balance()
    return callback(result)

@app.route('/thsauto/position', methods = ['GET'])
@interval_call
def get_position():
    auto.active_mian_window()
    result = auto.get_position()
    print(result)

    return callback(result)

@app.route('/thsauto/orders/active', methods = ['GET'])
@interval_call
def get_active_orders():
    auto.active_mian_window()
    result = auto.get_active_orders()
    return callback(result)

@app.route('/thsauto/orders/filled', methods = ['GET'])
@interval_call
def get_filled_orders():
    auto.active_mian_window()
    result = auto.get_filled_orders()
    return callback(result)

@app.route('/thsauto/sell', methods = ['GET'])
@interval_call
def sell():
    auto.active_mian_window()
    stock = request.args['stock_no']
    amount = request.args['amount']
    price = request.args.get('price', None)
    if price is not None:
        price = float(price)
    result = auto.sell(stock_no=stock, amount=int(amount), price=price)
    return callback(result)

@app.route('/thsauto/sellnowprice', methods = ['GET'])
@interval_call
def sellnowprice():
    auto.active_mian_window()
    stock = request.args['stock_no']
    amount = request.args['amount']

    hqarr = realHq.getReal(stock)
    price = hqarr[3]
    if price is not None:
        price = float(price)
    result = auto.sell(stock_no=stock, amount=int(amount), price=price)
    return callback(result)


@app.route('/thsauto/buy', methods = ['GET'])
@interval_call
def buy():
    auto.active_mian_window()
    stock = request.args['stock_no']
    amount = request.args['amount']
    price = request.args.get('price', None)
    if price is not None:
        price = float(price)
    result = auto.buy(stock_no=stock, amount=int(amount), price=price)
    return callback(result)




@app.route('/thsauto/buy/kc', methods = ['GET'])
@interval_call
def buy_kc():
    auto.active_mian_window()
    stock = request.args['stock_no']
    amount = request.args['amount']
    price = request.args.get('price', None)
    if price is not None:
        price = float(price)
    result = auto.buy_kc(stock_no=stock, amount=int(amount), price=price)
    return callback(result)

@app.route('/thsauto/sell/kc', methods = ['GET'])
@interval_call
def sell_kc():
    auto.active_mian_window()
    stock = request.args['stock_no']
    amount = request.args['amount']
    price = request.args.get('price', None)
    if price is not None:
        price = float(price)
    result = auto.sell_kc(stock_no=stock, amount=int(amount), price=price)
    return callback(result)

@app.route('/thsauto/cancel', methods = ['GET'])
@interval_call
def cancel():
    auto.active_mian_window()
    entrust_no = request.args['entrust_no']
    result = auto.cancel(entrust_no=entrust_no)
    return callback(result)

@app.route('/thsauto/cancelquick', methods = ['GET'])
@interval_call
def cancelquick():
    auto.active_mian_window()
    backflag = request.args['backflag']
    print(backflag)
    result = auto.cancelquick(backflag)
    return callback(result)


@app.route('/thsauto/client/kill', methods = ['GET'])
@interval_call
def kill_client():
    auto.active_mian_window()
    auto.kill_client()
    result = "{'code': 0, 'status': 'succeed'}"
    return callback(result)


@app.route('/thsauto/client/restart', methods = ['GET'])
@interval_call
def restart_client():
    auto.active_mian_window()
    auto.kill_client()
    run_client()
    time.sleep(5)
    auto.bind_client()
    if auto.hwnd_main is None:
        result = "{'code': 1, 'status': 'failed'}"
    else:
        result = "{'code': 0, 'status': 'succeed'}"
    return callback(result)

@app.route('/thsauto/test', methods = ['GET'])
@interval_call
def test():
    auto.active_mian_window()
    auto.test()
    return jsonify({}), 200


if __name__ == '__main__':
    host = '0.0.0.0'
    port = 5000
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    if len(sys.argv) > 3:
        client_path = sys.argv[3]
    auto.bind_client()
    if auto.hwnd_main is None and client_path is not None:
        restart_client()
    app.run(host=host, port=port)
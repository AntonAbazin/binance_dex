from binance_chain.http import HttpApiClient
from binance_chain.wallet import Wallet
from binance_chain.messages import NewOrderMsg, CancelOrderMsg, OrderType, OrderSide, TimeInForce
from binance_chain.environment import BinanceEnvironment
from aiohttp import web
import json


env = BinanceEnvironment.get_production_env()
client = HttpApiClient(env=env)


async def handle_post(request):
    data = await request.json()
    action = data.get('action')
    resp = None

    if action == 'time':
        resp = client.get_time()

    elif action == 'new_order':
        wallet = Wallet(data.get('private_key'), env=env)
        if data.get('side') == 'buy':
            side = OrderSide.BUY
        else:
            side = OrderSide.SELL
        msg = NewOrderMsg(
            wallet=wallet,
            symbol=data.get('symbol'),
            time_in_force=TimeInForce.GOOD_TILL_EXPIRE,
            order_type=OrderType.LIMIT,
            side=side,
            price=data.get('price'),
            quantity=data.get('quantity')
        )
        resp = client.broadcast_msg(msg, sync=True)

    elif action == 'canel_order':
        wallet = Wallet(data.get('private_key'), env=env)
        msg = CancelOrderMsg(
            wallet=wallet,
            order_id=data.get('order_id'),
            symbol=data.get('symbol'),
        )
        resp = client.broadcast_msg(msg, sync=True)

    if resp:
        body = json.dumps(resp)
        return web.Response(body=body, status=200)
    else:
        return web.Response(body='{"error": "wrong action"}', status=503)


async def handle_get(request):
    return web.Response(body='OK', status=200)


app = web.Application(client_max_size=(1024**2)*10)
app.router.add_post('/', handle_post)
app.router.add_get('/', handle_get)

web.run_app(app, port=55005)

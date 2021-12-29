import traceback, datetime
from flask import Blueprint, request, jsonify
from data.dataaccess import DataAccess
from data.ordersrepository import OrdersRepository

orders_api = Blueprint('orders_api',__name__)
db = DataAccess()
orderrepo = OrdersRepository(db)

@orders_api.route('/api/orders/<pagesize>/<pageno>/<sort>/<sortdir>', methods=["POST"])
def getOrders(pagesize='10', pageno='1',sort='createdat',sortdir='desc'):
    try:
        filters = []
        if len(request.json) >0:
            for f in request.json['filters']:
                filters.append(translateFilter(f))
        orders,totalcount = orderrepo.fetchOrders(int(pageno),int(pagesize), sort, sortdir, filters)
        return jsonify(success=True, totalcount=totalcount, data=orders)
    except Exception:
        return jsonify(success=False, message="Exception: " +traceback.format_exc()),500

@orders_api.route('/api/orders/products', methods=["GET"])
def getOrderProducts():
    products = orderrepo.getOrderProducts()
    return jsonify(success=True, data=products)

def translateFilter(filter):
    if filter['name']=='Product':
        filter['name'] = 'p.name'
    if filter['name'] == 'Timestamp':
        filter['name'] = 'o.createdat'
        filter['value'] = getInterval(filter['value'])
        filter['operator'] = '>'

    return filter

def getInterval(interval):
    now = datetime.datetime.now()
    mapping = {
        "1m":  datetime.timedelta(minutes=-1),
        "15m":  datetime.timedelta(minutes=-15),
        "1h":  datetime.timedelta(hours=-1),
        "6h":  datetime.timedelta(hours=-6),
        "1d":  datetime.timedelta(days=1),
        "1w":  datetime.timedelta(weeks=1),
    }
    return now + mapping[interval]
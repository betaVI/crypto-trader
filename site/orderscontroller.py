import os, time, traceback
from __main__ import app, db
from flask import Flask, request, jsonify, render_template
from data.ordersrepository import OrdersRepository

orderrepo = OrdersRepository(db)

@app.route('/api/orders/<pagesize>/<pageno>/<sort>/<sortdir>', methods=["GET"])
def getOrders(pagesize='10', pageno='1',sort='createdat',sortdir='desc'):
    try:
        orders,totalcount = orderrepo.fetchOrders(int(pageno),int(pagesize), sort, sortdir)
        return jsonify(success=True, totalcount=totalcount, data=orders)
    except Exception:
        return jsonify(success=False, message="Exception: " +traceback.format_exc()),500
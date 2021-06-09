import traceback
import dateutil.relativedelta
from datetime import datetime, timedelta
from __main__ import app, db
from flask import Flask, jsonify, request
from data.reportrepository import ReportRepository

reportrepo = ReportRepository(db)

@app.route('/api/reports/profit',methods=["GET"])
def getProductProfit():
    try:
        dates = [((datetime.now().replace(day=1) + dateutil.relativedelta.relativedelta(months=-i)).strftime('%m/%Y')) for i in range(6)]
        profits = reportrepo.getProductProfit()
        products = list(set([p['product'] for p in profits]))
        data = []
        for p in products:
            values = []
            for d in dates:
                values.append(next(iter([profit['netprofit'] for profit in profits if profit['product']==p and profit['month']==d]), 0))
            data.append({ 'product':p,'values':values})
        return jsonify(success=True, dates=dates, data=data)
    except Exception:
        return jsonify(success=False, message=traceback.format_exc())
import traceback
from __main__ import app, db
from flask import Flask, jsonify, request
from data.reportrepository import ReportRepository

reportrepo = ReportRepository(db)

@app.route('/api/reports/profit',methods=["GET"])
def getProductProfit():
    try:
        products = reportrepo.getProductProfit()
        return jsonify(success=True, data=products)
    except Exception:
        return jsonify(success=False, message=traceback.format_exc())
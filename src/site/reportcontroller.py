import traceback
import dateutil.relativedelta
from dependency_injector.wiring import Provide, inject
from datetime import datetime
from flask import Blueprint, jsonify
from src.container import Container
from src.data.reportrepository import ReportRepository

reports_api = Blueprint('reports_api',__name__)

@reports_api.route('/api/reports/profit',methods=["GET"])
@inject
def getProductProfit(reportrepo: ReportRepository = Provide[Container.report_repo]):
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
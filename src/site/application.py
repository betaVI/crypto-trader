import os, decimal, flask.json
from flask import Flask
from src.container import create_container

class JsonEncoder(flask.json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        return super(JsonEncoder, self).default()

def create_app() -> Flask:
    print('cwd is %s' %(os.getcwd()))

    from src.site.maincontroller import main_api
    from src.site.traderscontroller import trader_api
    from src.site.reportcontroller import reports_api
    from src.site.orderscontroller import orders_api
    from src.site.logscontroller import logs_api
    container = create_container(__name__)

    app = Flask(__name__)
    app.json_encoder = JsonEncoder
    app.container = container
    app.config['SECRET_KEY'] = str(os.urandom(32))

    app.register_blueprint(main_api)
    app.register_blueprint(trader_api)
    app.register_blueprint(reports_api)
    app.register_blueprint(orders_api)
    app.register_blueprint(logs_api)
    return app

# if __name__ == '__main__':
#     create_app().run(debug=True, port=18256, host='0.0.0.0')
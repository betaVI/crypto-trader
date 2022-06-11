import sys
from dependency_injector import containers, providers
from src.data.dataaccess import DataAccess
from src.data.logsrepository import LogsRepository
from src.data.ordersrepository import OrdersRepository
from src.data.reportrepository import ReportRepository
from src.data.testcbdataaccess import TestCbDataAccess
from src.data.traderrepository import TraderRepository
from src.services.cpapi import CbApi
from src.services.testcpapi import TestCbApi

class Container(containers.DeclarativeContainer):

    # wiring_config = containers.WiringConfiguration(modules=['src.bots.databot'], packages=['src.bots', 'src.data', 'src.services', 'src.site'])

    config = providers.Configuration()

    cbapi_client = providers.Factory(
        CbApi,
        key = config.cb.key,
        secret = config.cb.secret,
        passphrase = config.cb.passphrase,
        url = config.cb.url
    )

    db = providers.Singleton(
        DataAccess,
        host = config.db.host,
        port = config.db.port,
        dbname = config.db.database,
        user = config.db.user,
        password = config.db.password
    )

    logs_repo = providers.Singleton(
        LogsRepository,
        dataaccess = db
    )

    orders_repo = providers.Singleton(
        OrdersRepository,
        dataaccess = db
    )

    traders_repo = providers.Singleton(
        TraderRepository,
        dataaccess = db
    )

    report_repo = providers.Singleton(
        ReportRepository,
        dataaccess = db
    )

    testcb_db = providers.Singleton(
        TestCbDataAccess,
        host = config.testcbdb.host,
        port = config.testcbdb.port,
        database = config.testcbdb.database,
        user = config.testcbdb.user,
        password = config.testcbdb.password
    )

def create_container(module_name):
    container = Container()
    container.init_resources()
    container.wire(packages=[module_name, 'src.bots', 'src.data', 'src.services', 'src.site'])

    container.config.environment.from_env("ENVIRONMENT", as_=str, required=True)

    if not container.config.environment == 'PROD':
        container.cbapi_client.override(providers.Singleton(
            TestCbApi,
            key = container.config.cb.key,
            secret = container.config.cb.secret,
            passphrase = container.config.cb.passphrase,
            url = container.config.cb.url,
            db = container.testcb_db
        ))

    container.config.cb.key.from_env('CB_KEY', as_=str, required=True)
    container.config.cb.secret.from_env('CB_SECRET', as_=str, required=True)
    container.config.cb.passphrase.from_env('CB_PASSPHRASE', as_=str, required=True)
    container.config.cb.url.from_env('CB_URL', as_=str, required=True)
    
    container.config.db.host.from_env('PG_HOST', as_=str, required=True)
    container.config.db.port.from_env('PG_PORT', as_=str)
    container.config.db.database.from_env('PG_DATABASE', as_=str, required=True)
    container.config.db.user.from_env('PG_USER', as_=str, required=True)
    container.config.db.password.from_env('PG_PASSWORD', as_=str, required=True)

    container.config.testcbdb.host.from_env('PG_TESTCB_HOST', as_=str, required=True)
    container.config.testcbdb.port.from_env('PG_TESTCB_PORT', as_=str)
    container.config.testcbdb.database.from_env('PG_TESTCB_DATABASE', as_=str, required=True)
    container.config.testcbdb.user.from_env('PG_TESTCB_USER', as_=str, required=True)
    container.config.testcbdb.password.from_env('PG_TESTCB_PASSWORD', as_=str, required=True)

    return container
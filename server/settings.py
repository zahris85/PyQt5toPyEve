from eve_sqlalchemy.config import DomainConfig, ResourceConfig

from simple.tables import Invoices, People

DEBUG = True
SQLALCHEMY_DATABASE_URI = 'sqlite:////home/zahris/DATA/Projects/PyQt/server/data.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
RESOURCE_METHODS = ['GET', 'POST', 'DELETE']
ITEM_METHODS = ['GET', 'PATCH', 'DELETE', 'PUT']
# MONGO_QUERY_BLACKLIST = ['$where']
# IF_MATCH = True

# The following two lines will output the SQL statements executed by
# SQLAlchemy. This is useful while debugging and in development, but is turned
# off by default.
# --------
# SQLALCHEMY_ECHO = True
# SQLALCHEMY_RECORD_QUERIES = True

# The default schema is generated using DomainConfig:
DOMAIN = DomainConfig({
    'people': ResourceConfig(People),
    'invoices': ResourceConfig(Invoices)
}).render()

# But you can always customize it:
DOMAIN['people'].update({
    'item_title': 'person',
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,
    'resource_methods': ['GET', 'POST', 'DELETE'],
    'item_methods' : ['GET', 'PATCH', 'DELETE', 'PUT']
    # 'if_match': True
})

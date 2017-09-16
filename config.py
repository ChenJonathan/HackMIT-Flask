class Config(object):
    MYSQL_DATABASE_USER = 'sql9194895'
    MYSQL_DATABASE_PASSWORD = '312pj5NRdZ'
    MYSQL_DATABASE_DB = 'sql9194895'
    MYSQL_DATABASE_HOST = 'sql9.freemysqlhosting.net'

# hackmit2017.pythonanywhere.com
class ProductionConfig(Config):
    ENV = "Prod"

    MYSQL_DATABASE_USER = 'hackmit2017'
    MYSQL_DATABASE_PASSWORD = 'MITdb123'
    MYSQL_DATABASE_DB = 'hackmit2017$default'
    MYSQL_DATABASE_HOST = 'hackmit2017.mysql.pythonanywhere-services.com'

# 127.0.0.1:5000
class DevelopmentConfig(Config):
    ENV = "Dev"
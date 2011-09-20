class Config(object):
    SITE_TITLE = 'Celeb Site'
    SITE_NAME = 'Celeb Site'
    SITE_AUTHOR = 'Site Operators'
    GALLERIES_PER_PAGE = 6
    IMAGES_PER_PAGE = 9
    SECRET_KEY = '#\xfa\xaas\\\xf1\xbc\xd8\xf8\x05*\xa5\x80\x9e!f'
    UPLOAD_PATH = 'static/uploads/images'
    GOOGLE_ANALYTICS_UA = 'change me'


class ConfigDebug(Config):
    DEBUG = True
    EXTERNAL = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/celeb_debug.db'


class ConfigProduction(Config):
    DEBUG = False
    EXTERNAL = True
    EXTERNAL_HOST = '192.168.0.1'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///celeb_site.db'

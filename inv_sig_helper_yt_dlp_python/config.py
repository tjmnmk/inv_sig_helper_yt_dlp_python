import os

import const

class Config:
    def __init__(self):
        pass

    def get_host(self):
        default_host = const.DEFAULT_HOST
        host = os.environ.get(const.ENV_HOST, default_host)
        return host
    
    def get_port(self):
        default_port = const.DEFAULT_PORT
        port = os.environ.get(const.ENV_PORT, default_port)
        return port
    
    def get_log_level(self):
        default_log_level = const.LOG_LEVEL_DEFAULT
        log_level = os.environ.get(const.ENV_LOG_LEVEL, default_log_level)
        return log_level.upper()
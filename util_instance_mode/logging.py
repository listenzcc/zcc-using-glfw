from loguru import logger

logger.add('log/debug.log', level='DEBUG',
           rotation='1 MB', retention='10 days')

logger.add('log/info.log', level='INFO',
           rotation='1 MB', retention='10 days')

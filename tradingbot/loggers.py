import logging
import sys
from logging import Formatter
from logging.handlers import BufferingHandler, RotatingFileHandler, SysLogHandler
from typing import Any, Dict

from tradingbot.exceptions import OperationalException

logger = logging.getLogger(__name__)
LOGFROMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Intialize bufferhandler - will be used for /log endpoints
bufferHandler = BufferingHandler(1000)
bufferHandler.setFormatter(Formatter(LOGFROMAT))


def _set_loggers(verbosity: int = 0, api_verbosity: str = 'info') -> None:
    """
    Set the loggin level for third party libraries
    :return: None
    """

    logging.getLogger('request').setLevel(
        logging.INFO if verbosity <= 1 else logging.DEBUG)

    logging.getLogger('urllib3').setLevel(
        logging.INFO if verbosity <= 1 else logging.DEBUG)

    logging.getLogger('ccxt.base.echange').setLevel(
        logging.INFO if verbosity <= 2 else logging.DEBUG)

    logging.getLogger('telegram').setLevel(logging.INFO)

    logging.getLogger('werkzeug').setLevel(logging.ERROR if api_verbosity ==
                                           'error' else logging.INFO)


def setup_logging_pre() -> None:
    """
    Early setup for logging.
    Uses INFO loglevel and only the Streamhandler.
    Early messages (before proper logging setup) will therefore only be sent to addtional
    logging handlers after the real intialization, becuase we don't know which
    ones the user desires beforehand
    """

    logging.basicConfig(
        level=logging.INFO,
        format=LOGFROMAT,
        handlers=[logging.StreamHandler(sys.stderr), bufferHandler])


def setup_logging(config: Dict[str, Any]) -> None:
    """
    Process -v/ --verbose, --logfile options
    """
    # Log level
    verbosity = config['verbosity']

    logging.root.addHandler(bufferHandler)

    logfile = config.get('logfile')

    if logfile:
        s = logfile.split(':')
        if s[0] == 'syslog':
            # Address can be either as string (socket filename) for Unix domain socker or
            # a tuple (hostname, port) for UDP socket.
            # Address can be omitted (i.e. simple 'syslog' used as the value of
            # config['logfilename'], which defults to '/dev/log', applicable for most
            # of the systems
            address = (s[1], int(
                s[2])) if len(s) > 2 else s[1] if len(s) > 1 else '/dev/log'
            handler = SysLogHandler(address=address)
            # No datetime field for logging into syslog,to allow syslog
            # to perform reduction of repeating messages if this is set in the
            # syslog config. The messages should be equal for this.

            handler.setFormatter(
                Formatter('%(name)s - %(levelname)s - %(message)s'))
            logging.root.addHandler(handler)
        elif s[0] == 'journald':
            try:
                from systemd.journal import JournaldLogHandler
            except ImportError:
                raise OperationalException(
                    "You need the systemd python package be installed in "
                    "order to use logging to journald.")
            handler_jd = JournaldLogHandler()
            # No datetime field for logging into journald, to allow syslog
            # to perform reduction of repeating messages if this is set in the
            # syslog config. The messages should be equal for this.
            handler_jd.setFormatter(
                Formatter('%(name)s - %(levelname)s - %(message)s'))
            logging.root.addHandler(handler_jd)

        else:
            handler_rf = RotatingFileHandler(
                logfile,
                maxBytes=1024 * 1024 * 10,  # 10Mb,
                backupCount=10)
            handler_rf.setFormatter(Formatter(LOGFROMAT))
            logging.root.addHandler(handler_rf)

    logging.root.setLevel(logging.INFO if verbosity < 1 else logging.DEBUG)
    _set_loggers(verbosity,
                 config.get('api_server', {}).get('verbosity', 'info'))
    logger.info('Verbosity set to %s', verbosity)

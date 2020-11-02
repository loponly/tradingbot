from tradingbot.commands import cli_options
from tradingbot.loggers import *

option = cli_options.AVAILABLE_CLI_OPTIONS['hyperopt_show_no_header']

if __name__ == "__main__":
    print(bufferHandler)
    config = {'logfile': 'first.log', 'api_server': {}, 'verbosity': 0}
    setup_logging(config)
    logging.info('Sup bro')
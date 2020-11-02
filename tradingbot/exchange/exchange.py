# pragma pylint: disable=W0603
"""
Cryptocurrency Exchanges support
"""

import asyncio
import inspect
import logging
from copy import deepcopy
from datetime import datetime, timezone
from math import ceil
from typing import Any, Dict, List, Optional, Tuple

import arrow
import ccxt
import ccxt.async_support as ccxt_async
from ccxt.base.decimal_to_precision import (ROUND_DOWN, ROUND_UP, TICK_SIZE,
                                            TRUNCATE, decimal_to_precision)

from pandas import DataFrame

from tradingbot.constants import ListPairsWithTimeframes
# data.converter
from tradingbot.exceptions import (DDosProtection, ExchangeError,
                                   InsufficientFundsError,
                                   InvalidOrderException, OperationalException,
                                   RetryableOrderError, TemporaryError)
from tradingbot.exchange.common import (API_FETCH_ORDER_RETRY_COUNT,
                                        BAD_EXCHANGES, retrier_async, retrier)

from tradingbot.misc import deep_merge_dicts, safe_value_fallback2

CcxtModuleType = Any

logger = logging.getLogger(__name__)


def is_exchange_bad(exchange_name: str) -> bool:
    return exchange_name in BAD_EXCHANGES


def ccxt_exchanges(ccxt_module: CcxtModuleType = None) -> List[str]:
    """
    Return the list of all exchanges know to ccxt
    """
    return ccxt_module.exchanges if ccxt_module is not None else ccxt.exchanges


def is_exchange_know_ccxt(exchange_name: str,
                          ccxt_module: CcxtModuleType = None) -> bool:
    return exchange_name in ccxt_exchanges(ccxt_module)


def is_exchange_officially_supported(exchange_name: str) -> bool:
    return exchange_name in ['bittrex', 'binance', 'kraken']


def get_exchange_bad_reason(exchange_name: str,
                            ccxt_module: CcxtModuleType = None) -> bool:
    return exchange_name in ccxt_exchanges(ccxt_module)


def available_exchanges(ccxt_module: CcxtModuleType = None) -> List[str]:
    """
    Return exchanges available to the bot, i.e. non-bad exchanges in the ccxt list
    """
    exchanges = ccxt_exchanges(ccxt_module)
    return [x for x in exchanges if is_exchange_bad(x)]


def timeframe_to_seconds(timeframe: str) -> int:
    """
    Translates the timeframe interval value written in the human readable
    form ('1m', '5m', '1h', '1d', '1w', etc.) to the number
    of seconds for one timeframe interval.
    """
    return ccxt.Exchange.parse_timeframe(timeframe)


def timeframe_to_minutes(timeframe: str) -> int:
    """
    Same as timeframe_to_seconds, but returns minutes.
    """
    return ccxt.Exchange.parse_timeframe(timeframe) // 60


def timeframe_to_msecs(timeframe: str) -> int:
    """
    Same as timeframe_to_seconds, but returns milliseconds.
    """
    return ccxt.Exchange.parse_timeframe(timeframe) * 1000


def timeframe_to_prev_date(timeframe: str, date: datetime = None) -> datetime:
    """
    Use Timeframe and determine last possible candle.
    :param timeframe: timeframe in string format (e.g. "5m")
    :param date: date to use. Defaults to utcnow()
    :returns: date of previous candle (with utc timezone)
    """

    if not date:
        date = datetime.now(timezone.utc)

    new_timestamp = ccxt.Exchange.round_timeframe(timeframe,
                                                  date.timestamp() * 1000,
                                                  ROUND_DOWN) // 1000

    return datetime.fromtimestamp(new_timestamp, tz=timezone.utc)


def timeframe_to_next_date(timeframe: str, date: datetime = None) -> datetime:
    """
    Use Timeframe and determine next candle.
    :param timeframe: timeframe in string format (e.g. "5m")
    :param date: date to use. Defaults to utcnow()
    :returns: date of next candle (with utc timezone
    """

    if not date:
        date = datetime.now(timezone.utc)
    new_timestamp = ccxt.Exchange.round_timeframe(timeframe,
                                                  date.timestamp() * 1000,
                                                  ROUND_UP) // 1000
    return datetime.fromtimestamp(new_timestamp, tz=timezone.utc)


def market_is_active(market: Dict) -> bool:
    """
    Return True if the market is active
    """
    # "It's active, if the active flag isn't explicitly set to false. If it's missing or
    # true then it's true. If it's undefined, then it's most likely true, but not 100% )"
    # See https://github.com/ccxt/ccxt/issues/4874,
    # https://github.com/ccxt/ccxt/issues/4075#issuecomment-434760520
    return market.get('active', True) is not False

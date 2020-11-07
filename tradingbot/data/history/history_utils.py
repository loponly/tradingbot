import logging
import operator
from datetime import datetime, timezone
from pathlib import Path

from typing import Dict, List, Optional, Tuple

import arrow
from pandas import DataFrame

from tradingbot.configuration import TimeRange
from tradingbot.constants import DEFAULT_DATAFRAME_COLUMNS
from tradingbot.data.converter import (clean_ohlcv_dataframe,
                                       ohlcv_to_dataframe,
                                       trades_remove_duplicates,
                                       trades_to_ohlcv)
from tradingbot.data.history.idatahandler import IDataHandler, get_datahandler
from tradingbot.exceptions import OperationalException
# from tradingbot.exchange import

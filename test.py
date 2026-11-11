import os
import atexit
from pathlib import Path
from writers.test_csv import make_test_csv, remove_rows_where

TEST_BID_ENV = 'TEST_BANNER_ID'
TEST_CSV = 'test.csv'
TEST_COL = 'bid'

def get_test_bid(bid_env_var=TEST_BID_ENV) -> str | None:
    test_bid = os.environ.get(bid_env_var)
    if test_bid is None:
        print(f'  ! {bid_env_var} not found in .env')
        return None
    return test_bid

def cleanup_test_mode(bid_env_var=TEST_BID_ENV, test_file: str | Path = TEST_CSV):
    print(f'+ cleaning up test mode - removing {bid_env_var} from {test_file}')
    removed = remove_rows_where(test_file, TEST_COL, get_test_bid(bid_env_var))
    print(f'  + removed {removed} rows containing {bid_env_var} from {test_file}')

def setup_test_mode(bid_env_var=TEST_BID_ENV) -> str | None:
    print(f'+ test mode - adding {bid_env_var} from .env file to {TEST_CSV}')
    test_bid = get_test_bid(bid_env_var)
    path = make_test_csv([TEST_COL], [[test_bid]])
    print(f'  + wrote {bid_env_var} to {path}')
    atexit.register(cleanup_test_mode, bid_env_var, path)
    return test_bid

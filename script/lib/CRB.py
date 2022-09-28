from datetime import datetime
from locale import atof

import httplib2

from .config import (REQUEST_TIMEOUT, VALUTE_CHAR_CODE,
                     VALUTE_INFO_NOMINAL_CLOSE_TAG,
                     VALUTE_INFO_NOMINAL_OPEN_TAG, VALUTE_INFO_OPEN_TAG,
                     VALUTE_INFO_VALUE_CLOSE_TAG, VALUTE_INFO_VALUE_OPEN_TAG)


class CRB:
    def __init__(self):
        self.client = httplib2.Http(timeout=REQUEST_TIMEOUT)
        self.currency_rate = 0
        self.fetch_currency_rate()

    def fetch_currency_rate(self):
        # API call example
        # http://www.cbr.ru/scripts/XML_daily.asp?date_req=02/03/2002

        try:
            cbr_response, cbr_response_s = self.client.request(
                f'http://www.cbr.ru/scripts/XML_daily.asp?date_req={datetime.now().strftime("%d/%m/%Y")}',
                'GET',
            )
            cbr_response_s = str(cbr_response_s)

            if cbr_response.get('status') != '200':
                print('Error fetching currency from http://www.cbr.ru/ :\n\t',
                      cbr_response_s)

            try:
                # can use beautiful soup instead
                start_charcode_idx = cbr_response_s.index(
                    VALUTE_INFO_OPEN_TAG + VALUTE_CHAR_CODE) + len(
                    VALUTE_INFO_OPEN_TAG + VALUTE_CHAR_CODE)
                start_value_idx = cbr_response_s.index(
                    VALUTE_INFO_VALUE_OPEN_TAG, start_charcode_idx) + len(
                    VALUTE_INFO_VALUE_OPEN_TAG)
                end_value_idx = cbr_response_s.index(
                    VALUTE_INFO_VALUE_CLOSE_TAG, start_value_idx)
                start_nominal_idx = cbr_response_s.index(
                    VALUTE_INFO_NOMINAL_OPEN_TAG) + len(
                    VALUTE_INFO_NOMINAL_OPEN_TAG)
                end_nominal_idx = cbr_response_s.index(
                    VALUTE_INFO_NOMINAL_CLOSE_TAG, start_nominal_idx)
                currency_rate = cbr_response_s[start_value_idx: end_value_idx]
                nominal = cbr_response_s[start_nominal_idx: end_nominal_idx]
                self.currency_rate = atof(
                    currency_rate.replace(',', '.')) / atof(
                    nominal.replace(',', '.'))
            except ValueError:
                print(
                    f'Error: unable to fetch {VALUTE_CHAR_CODE} currency rate. The CBR API has changed')


        except Exception as e:
            print(f'Error: unable to fetch {VALUTE_CHAR_CODE} currency rate:',
                  e)
        finally:
            return self.currency_rate


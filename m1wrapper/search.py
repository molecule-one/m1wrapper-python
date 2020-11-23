import requests
import json
import time
from typing import List
from urllib.parse import urljoin

from .config import (
    api_search_endpoint,
    api_results_endpoint,
    status_check_delay_s
)


def format_error_message(error):
    if error["message"] and error["errors"]:
        return f'{error["message"]}: {repr(error["errors"])}'
    if error["message"]:
        return f'{error["message"]}'
    else:
        return "unknown error"


def maybe_handle_error(response):
    if response.status_code >= 400 and response.status_code <= 500:
        error = format_error_message(response.json())
        raise requests.exceptions.HTTPError(error)
    else:
        response.raise_for_status()


class BatchSearch:
    def __init__(
        self,
        base_url,
        headers,
        search_id=None,
        targets=None,
        parameters=None,
    ):
        self.search_id = search_id
        self.base_url = base_url
        self.headers = headers
        if self.search_id is None:
            new_search = self.__run(targets=targets, parameters=parameters)
            self.search_id = new_search['id']

    def __prepare_payload(self, targets, parameters) -> dict:
        return {
            'targets': targets,
            'params': parameters or {},
        }

    def __run(self, targets, parameters):
        payload = self.__prepare_payload(targets, parameters)
        response = requests.post(
            urljoin(self.base_url, api_search_endpoint),
            data=json.dumps(payload),
            headers=self.headers,
        )
        maybe_handle_error(response)
        return response.json()

    @classmethod
    def from_id(cls, base_url, headers, search_id):
        return cls(base_url, headers, search_id)

    def get_status(self):
        response = requests.get(
            urljoin(self.base_url, f'{api_search_endpoint}/{self.search_id}'),
            headers=self.headers,
        )
        maybe_handle_error(response)
        return response.json()

    def is_finished(self):
        status = self.get_status()
        return status['queued'] == 0 and status['running'] == 0

    def get_results(
            self,
            precision: int = None,
            only: List[str] = None
    ):
        while self.is_finished() is False:
            time.sleep(status_check_delay_s)

        return self.get_partial_results(precision, only)

    def get_partial_results(
        self,
        precision: int = None,
        only: List[str] = None
    ):
        response = requests.get(
            urljoin(self.base_url, f'{api_results_endpoint}/{self.search_id}'),
            headers=self.headers,
            params={
                'precision': precision,
                'only': only
            }
        )
        maybe_handle_error(response)
        return response.json()

    def delete(self):
        response = requests.delete(
            urljoin(self.base_url, f'{api_search_endpoint}/{self.search_id}'),
            headers=self.headers,
        )
        maybe_handle_error(response)
        return True

import requests
import json
import time
import logging
import urllib3
from typing import List
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
urllib3.add_stderr_logger(logging.WARNING)

from .traverse import traverse_modify

from .config import (
    api_search_endpoint,
    api_status_endpoint,
    api_results_endpoint,
    status_check_delay_s,
    http_backoff_factor,
    http_retries,
    http_retries_on_connect
)

from .errors import (
    maybe_handle_error
)

class BatchSearch:
    def __init__(
        self,
        base_url,
        headers,
        search_id=None,
        targets=None,
        parameters=None,
        detail_level=None,
        priority=None,
        invalid_target_strategy=None,
        preset=None,
        name=None,
        targets_metadata=None,
    ):
        self.search_id = search_id
        self.base_url = base_url
        self.headers = headers
        self.http = self.__prepare_http()
        if self.search_id is None:
            new_search = self.__run(
                    targets=targets,
                    parameters=parameters,
                    detail_level=detail_level,
                    priority=priority,
                    invalid_target_strategy=invalid_target_strategy,
                    preset=preset,
                    name=name,
                    targets_metadata=targets_metadata
            )
            self.search_id = new_search['id']

    def __prepare_payload(self, targets, parameters, detail_level, priority, invalid_target_strategy, preset, name, targets_metadata) -> dict:
        payload = {
            'targets': targets,
            'parameters': parameters or {},
            'detail_level': detail_level,
            'priority': priority,
            'invalid_target_strategy': invalid_target_strategy
        }
        if preset is not None:
            payload["preset"] = preset 
        if name is not None:
            payload["name"] = name
        if targets_metadata is not None:
            payload['targets_metadata'] = targets_metadata

        return payload

    def __prepare_http(self):
        retry_strategy = Retry(
            total=http_retries,
            connect=http_retries_on_connect,
            backoff_factor=http_backoff_factor,
            status_forcelist=[104, 111, 429, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "DELETE", "PUT"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        http = requests.Session()
        http.mount("https://", adapter)
        http.mount("http://", adapter)
        return http

    def __run(self, targets, parameters, detail_level, priority, invalid_target_strategy, preset, name, targets_metadata):
        payload = self.__prepare_payload(targets, parameters, detail_level, priority, invalid_target_strategy, preset, name, targets_metadata)
        response = self.http.post(
            urljoin(self.base_url, api_search_endpoint),
            data=json.dumps(payload),
            headers=self.headers,
        )
        maybe_handle_error(response)
        return response.json()

    @classmethod
    def from_id(cls, base_url, headers, search_id):
        return cls(base_url, headers, search_id)

    def get(self):
        response = self.http.get(
            urljoin(self.base_url, f'{api_search_endpoint}/{self.search_id}'),
            headers=self.headers,
        )
        maybe_handle_error(response)
        return response.json()

    def get_status(self):
        response = self.http.get(
            urljoin(self.base_url, f'{api_status_endpoint}/{self.search_id}'),
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
        response = self.http.get(
            urljoin(self.base_url, f'{api_results_endpoint}/{self.search_id}'),
            headers=self.headers,
            params={
                'precision': precision,
                'only': only
            }
        )
        maybe_handle_error(response)
        results = response.json()

        if precision is None:
            return results

        precision_str = '.' + str(precision) + 'f'
        results = traverse_modify(results, '[].result', lambda el: format(float(el), precision_str) if el else el)
        results = traverse_modify(results, '[].certainty', lambda el: format(float(el), precision_str) if el else el)
        results = traverse_modify(results, '[].price', lambda el: format(float(el), precision_str) if el else el)
        return results

    def delete(self):
        response = self.http.delete(
            urljoin(self.base_url, f'{api_search_endpoint}/{self.search_id}'),
            headers=self.headers,
        )
        maybe_handle_error(response)
        return True

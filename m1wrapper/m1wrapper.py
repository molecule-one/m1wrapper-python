import requests
from urllib.parse import urljoin
from typing import List, Dict
from enum import Enum, IntEnum

from .search import BatchSearch
from .config import (
    api_token_version,
    wrapper_version,
    api_base_url,
    api_search_endpoint
)

from .errors import (
    maybe_handle_error
)

class Priority(IntEnum):
    LOWEST = 1,
    LOW = 3,
    NORMAL = 5,
    HIGH = 8,
    HIGHEST = 10

class DetailLevel(str, Enum):
    SCORE = 'score',
    SYNTHESIS = 'synthesis'

class InvalidTargetStrategy(str, Enum):
    REJECT = 'reject',
    PASS = 'pass'

class MoleculeOneWrapper:
    """
    Wrapper for MoleculeOne Batch Scoring REST API
    """

    def __init__(
        self,
        api_token: str,
        api_base_url: str = api_base_url
    ):
        self.api_token = api_token
        self.api_base_url = f'{api_base_url}/api/v2/'
        self.request_headers = self.__prepare_request_headers()

    def __prepare_request_headers(self) -> dict:
        return {
            'Content-Type': 'application/json',
            'User-Agent': f'api-wrapper-python/{wrapper_version}',
            'Authorization': f'ApiToken-{api_token_version} {self.api_token}'
        }
    
    def list_batch_searches(self):
        response = requests.get(
            urljoin(self.api_base_url, api_search_endpoint),
            headers=self.request_headers,
        )
        print(response)
        maybe_handle_error(response)
        return response.json()

    def run_batch_search(
            self,
            targets: List[str],
            parameters: Dict = None,
            detail_level = DetailLevel.SCORE,
            priority = Priority.NORMAL,
            invalid_target_strategy = InvalidTargetStrategy.REJECT ,
            starting_materials: List[str] = None,
    ) -> BatchSearch:
        return BatchSearch(
                self.api_base_url,
                self.request_headers,
                targets=targets,
                parameters=parameters,
                detail_level=detail_level,
                priority=int(priority),
                invalid_target_strategy=invalid_target_strategy,
                starting_materials=starting_materials
            )

    def get_batch_search(self, search_id: str) -> BatchSearch:
        search = BatchSearch.from_id(
                self.api_base_url,
                self.request_headers,
                search_id
        )
        data = search.get()
        return search

    def delete_batch_search(self, search_id: str):
        search = BatchSearch.from_id(
                self.api_base_url,
                self.request_headers,
                search_id
        )
        return search.delete()


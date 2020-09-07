import requests
import abc
from typing import List
from zeep import Client
from schemas import Query, MediaTypeEnum, SearchResults


class BaseClient(abc.ABC):
    name = None
    supported_types = []
    supported_filters = []
    base_url = None

    def execute_query(self, query: Query):
        if query.type in self.supported_types:
            return self._service_integration(query)
        else:
            return []

    @abc.abstractmethod
    def _service_integration(self, query: Query) -> List:
        raise NotImplemented("Please implement the service integration")


class ItunesClient(BaseClient):
    name = 'Itunes'
    supported_types = [MediaTypeEnum.movie, MediaTypeEnum.song]
    supported_filters = ['term', 'country']
    base_url = "https://itunes.apple.com"

    def _service_integration(self, query: Query) -> List:
        filter_object = query.filter
        params = {
            k: getattr(filter_object, k) for k in self.supported_filters if getattr(filter_object, k) is not None
        }
        params['entity'] = query.type
        r = requests.get(f"{self.base_url}/search", params=params)
        return r.json().get('results', [])


class TvMazeClient(BaseClient):
    name = 'Tv Maze'
    supported_types = [MediaTypeEnum.show]
    supported_filters = ['term', 'tvrage', 'thetvdb', 'imdb']
    base_url = 'http://api.tvmaze.com'

    def _service_integration(self, query: Query) -> List:
        results = []
        filter_object = query.filter

        # Search by id lookup
        # for id_name in ['tvrage', 'thetvdb', 'imdb']:
        for id_name in self.supported_filters.remove('term'):
            if getattr(filter_object, id_name):
                result = self._search_by_id(
                    id_name, getattr(filter_object, id_name))
                results.append(result)

        # Search by term
        if filter_object.term:
            results_by_term = requests.get(
                f'{self.base_url}/search/shows', params={'q': filter_object.term})
            results.append(results_by_term.json())

        return results

    def _search_by_id(self, id_name, id_value):
        r = requests.get(f'{self.base_url}/lookup/shows',
                         params={id_name: id_value})
        return r.json()


class CRCINDClient(BaseClient):
    name = "CRC Ind"
    supported_types = [MediaTypeEnum.person]
    supported_filters = ['term']
    base_url = 'http://www.crcind.com/csp/samples/SOAP.Demo.CLS?WSDL=1'

    def __init__(self):
        super().__init__()
        self.client = Client(self.base_url)

    def _service_integration(self, query: Query) -> List:
        filter_object = query.filter
        results = []
        for id_name in self.supported_filters:
            if getattr(filter_object, id_name):

                r = self.client.service.GetListByName(
                    getattr(filter_object, id_name))

                if not isinstance(r, list):
                    results.append(r)
                else:
                    results += r

        return results


class ClientProvider:
    __instance = None
    _clients: List[BaseClient] = []

    def __init__(self):
        for Client in BaseClient.__subclasses__():
            self._clients += [Client()]

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls.__instance = ClientProvider()
        return cls.__instance

    def launch_query(self, query: Query) -> List[SearchResults]:
        results = []
        for client in self._clients:
            client_results = client.execute_query(query)
            results.append(
                SearchResults(source=client.name,
                              results=client_results, count=len(client_results))
            )
        return results

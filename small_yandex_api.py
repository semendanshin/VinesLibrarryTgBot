import requests


class BaseAPI:
    def __init__(self, **default_params):
        self.base_url = None
        self.default_params = default_params

    def get(self, **params) -> requests.Response:
        return requests.get(
            url=self.base_url,
            params=self.default_params | params
        )


class GeoCoderAPI(BaseAPI):
    def __init__(self, **default_params):
        super().__init__(**default_params)
        self.base_url = 'https://geocode-maps.yandex.ru/1.x'


class StaticAPI(BaseAPI):
    def __init__(self, **default_params):
        super().__init__(**default_params)
        self.base_url = 'https://static-maps.yandex.ru/1.x/'


class OrganisationsAPI(BaseAPI):
    def __init__(self, **default_params):
        super().__init__(**default_params)
        self.base_url = 'https://search-maps.yandex.ru/v1/'

import pyoacore
from PyASS import ass_constant as constant
from pyoacore.rest import ApiException

_DESCRIPTION = "description"
_PUBLISHER = "publisher"
_REPOSITORIES_ID = "repositories.id"
_REPOSITORIES_NAME = "repositories.name"
_OAI = "oai"
_IDENTIFIERS = "identifiers"
_LANGUAGE_NAME = "language.name"
_YEAR = "year"

_QUERY_PARAMS = {
    constant.TITLE_TAG: "title",
    constant.AUTHOR_TAG: "authors",
    constant.DOI_TAG: "doi",
    constant.CONTENT_TAG: "fullText"
}


class CORE_scrapper:
    """
    The class that encapsulate request to CORE repository
    """
    def __init__(self):
        self._api_instance = pyoacore.ArticlesApi()

    def _request(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        if 'url' in kwargs:
            self._api_instance.api_client.request("POST", kwargs['url'])
        elif 'query' in kwargs:
            self._api_instance.articles_api_call("POST", params=kwargs['query'])

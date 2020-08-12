from bs4 import BeautifulSoup as bs
from PyASS import ass_constant


def load_jasss_article(self, volume=0, issue=0, articles=0):
    """
    scrap an article from JASSS as a 'soup'
    :param self: None
    :param volume: 
    :param issue:
    :param articles:
    :return:
    """
    basic_url = ass_constant.JASSS_BASE_URL + str(volume) \
                + ass_constant.JASSS_SEP + str(issue) \
                + ass_constant.JASSS_SEP
    req = bs.requests.get(basic_url + str(articles) + ".html")
    bs_article: bs.BeautifulSoup
    if req.status_code == bs.requests.codes.ok:
        bs_article = bs.BeautifulSoup(req.content, 'html5lib')
    else:
        bs_article = bs.BeautifulSoup(
            bs.requests.get(basic_url + str("review" + str(articles)) + ".html"),
            'html5lib')
    return req.url, bs_article

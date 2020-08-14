import os
import logging
from pathlib import Path
from bs4 import BeautifulSoup as bs
from re import findall as fall
from requests import HTTPError

from PyASS import ass_abstractions as ass

FROM_VOLUME = "from_volume"
TO_VOLUME = "to_volume"
FROM_ISSUE = "from_issue"
TO_ISSUE = "to_issue"
FROM_ARTICLE = "from_article"
TO_ARTICLE = "to_article"

SKIP_REVIEW = "skip review"
TO_FOLDER = "to_folder"

RVW = "review"

logging.basicConfig()
log = logging.getLogger("ass.jasss_scrape")
log.setLevel(logging.INFO)


class JASSS_Scrapper:
    """
    The main object to scap JASSS from the website
    """
    _JASSS_BASE_URL = "http://jasss.soc.surrey.ac.uk/"
    _JASSS_INDEX_URL = "http://jasss.soc.surrey.ac.uk/index_by_issue.html"
    _JASSS_SEP = '/'

    jasss_biblio_match = "References"

    _JASSS_META_TAG = "meta"
    _JASSS_META_NAME = "name"
    _JASSS_META_CONTENT = "content"

    _ART = {"title": "arttitle", "doi": "artdoi"}

    _META = {"title": "DC.Title", "authors": "DC.Creator", "abstract": ("DC.Description", "DC.Abstract"),
             "date": "DC.Date", "tags": "DC.Subject", "doi": "DC.Identifier.DOI"}

    def load_jasss_article(self, volume=0, issue=0, articles=0, url=None):
        """
        scrap an article from JASSS as a 'soup'
        :param self: None
        :param volume:
        :param issue:
        :param articles:
        :param url:
        :return: tuple url, soup
        """
        basic_url = self._JASSS_BASE_URL + str(volume) + self._JASSS_SEP + str(issue) + self._JASSS_SEP \
            if url is None else url
        req = bs.requests.get(basic_url + str(articles) + ".html")
        bs_article: bs.BeautifulSoup
        if req.status_code == bs.requests.codes.ok:
            bs_article = bs.BeautifulSoup(req.content, 'html5lib')
        else:
            bs_article = bs.BeautifulSoup(
                bs.requests.get(basic_url + str("review" + str(articles)) + ".html"),
                'html5lib')
        return req.url, bs_article

    def load_jasss_from_to(self, **kwargs) -> ass.ASSCorpus:
        """
        scrap JASSS
        :param self:
        :param kwargs:
         * from_volume -- int (default = 0)
         * from_issue -- int (default = 0)
         * from_article -- int (default = 0)
         * to_volume -- int (default = last)
         * to_issue -- int (default = last)
         * to_article -- int (default = last)
         * skip_review -- bool (default = False)
         * to_folder -- path (default = .tmp/)
        :return: ASSCorpus
        """
        fv = kwargs[FROM_VOLUME] if FROM_VOLUME in kwargs else 0
        fi = kwargs[FROM_ISSUE] if FROM_ISSUE in kwargs else 0
        fa = kwargs[FROM_ARTICLE] if FROM_ARTICLE in kwargs else 0
        tv = kwargs[TO_VOLUME] if TO_VOLUME in kwargs else -1
        ti = kwargs[TO_ISSUE] if TO_ISSUE in kwargs else -1
        ta = kwargs[TO_ARTICLE] if TO_ARTICLE in kwargs else -1
        sr = kwargs[SKIP_REVIEW] if SKIP_REVIEW in kwargs else False
        tp = kwargs[TO_FOLDER] if TO_FOLDER in kwargs else Path(os.getcwd() + "/data")
        corp = ass.ASSCorpus()

        req_text = bs.request.urlopen(url=self._JASSS_INDEX_URL).read()
        page = bs.BeautifulSoup(req_text, "lxml")
        nb_max = len(page.findAll("p", {'class': 'item'}))

        itr = 0
        rvw = 0
        for gen in page.findAll("p", {'class': 'item'}):
            itr += 1
            url_article = gen.find("a")['href']

            url_issue = [e for e in fall(r"[\w']+", url_article) if e.isdigit()]

            if url_issue == [str(tv), str(ti), str(ta)]:
                break

            prop = round(itr / nb_max * 100, 4)
            log.info(str(prop) + "% => " + url_article + " | " + str(url_issue) + " review = " + str(rvw))
            try:
                article = self.load_jasss_article(url=url_article)
            except HTTPError as e:
                print("Don't care about http request exceptions: ", e)

            if JASSS_Scrapper.is_review(article[0]):
                rvw += 1
                continue

            doi = article.doi()
            res_file = str(tp) + "/JASSS_" + JASSS_Scrapper.doi_converter(doi) + ".txt"
            os.makedirs(os.path.dirname(res_file), exist_ok=True)
            bib_file = str(tp) + "/JASSS_bib.txt"
            os.makedirs(os.path.dirname(bib_file), exist_ok=True)

            # TODO : save articles into a bib reference corpus

            article.save(res_file)
            if (itr % 10000000) == 0:
                inp = input("Type 'c' button to continue 'e' to exit")
                exit(0) if inp == 'e' else log.info("Carry on")

        return corp

    @staticmethod
    def get_issue_from_url(url) -> list:
        """
        Retrieve number of issue, volume, article
        :param url: the url to be inspected
        :return: a list of numbers
        """
        issue = str(url).split("/")
        return [issue[-3], issue[-2], issue[-1].replace(".html", "")]

    @staticmethod
    def is_review(url) -> bool:
        """
        Tells if this article is a review or not
        :param url: the url of the JASSS article
        :return: true if the soup represents a review false otherwise
        """
        return True if RVW in url or not JASSS_Scrapper.get_issue_from_url(url)[-1].isdigit() else False

    @staticmethod
    def doi(url, soup: bs.BeautifulSoup):
        """
        Give the DOI stored in meta data
        :return: a unique *string* that represent this article
        """
        if JASSS_Scrapper.is_review(url):
            return None
        try:
            doi = JASSS_Scrapper.get_meta_content_with_tag(soup, "doi")
        except TypeError:
            doi = JASSS_Scrapper.get_art_content_with_tag("doi")
        return doi if doi else JASSS_Scrapper.get_issue_from_url(url)

    @staticmethod
    def get_meta_content_with_tag(soup: bs.BeautifulSoup = None, tag="title"):
        """
        Retrieve the content of a tag as define by *beautifulsoup*
        :param BeautifulSoup soup: the soup to extract tag from
        :param str tag: the tag to find in the soup
        :return: a string representation of the content of the tag
        """
        if soup is None:
            raise TypeError("get_meta_constent_with_tag missing one required positional 1 argument: soup")
        m_name = JASSS_Scrapper._JASSS_META_NAME
        m_content = JASSS_Scrapper._JASSS_META_CONTENT
        if soup.find_next(JASSS_Scrapper._JASSS_META_TAG, {JASSS_Scrapper._JASSS_META_NAME.upper(): "title"}):
            m_name = JASSS_Scrapper._JASSS_META_NAME.upper()
            m_content = JASSS_Scrapper._JASSS_META_CONTENT.upper()

        if isinstance(JASSS_Scrapper._META[tag], str):
            meta_context = soup.find(JASSS_Scrapper._JASSS_META_TAG, {m_name: JASSS_Scrapper._META[tag]})
        else:
            for tg in JASSS_Scrapper._META[tag]:
                meta_context = soup.find(JASSS_Scrapper._JASSS_META_TAG, {m_name: tg})
                if meta_context is not None:
                    break
        return meta_context[m_content]

    @staticmethod
    def get_art_content_with_tag(soup: bs.BeautifulSoup = None, tag="title"):
        """
        Retrieve the content of a tag define in the *art* section of JASSS article pages
        :param BeautifulSoup soup: the soup to extract tag from
        :param str tag: the 'art' tag to find in the soup
        :return: a string representation of the content of the tag
        """
        if soup is None:
            raise TypeError("get_art_constent_with_tag missing one required positional 1 argument: soup")
        balise: str = "p"
        if tag == "doi":
            balise = "span"
        result = soup.find(balise, {'class': JASSS_Scrapper._ART[tag]})
        if result is None:
            if tag == "doi":
                return JASSS_Scrapper.doi(None, soup)
            else:
                return super().NA
        elif tag == "doi":
            result = result.contents[0].replace('DOI:', '') if result else super().NA
        return result.strip()
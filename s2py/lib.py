import re
from dataclasses import dataclass, field
from time import sleep, time
from typing import List, Optional, Tuple, cast
from urllib.parse import urlencode

import httpx
from fake_useragent import UserAgent
from parsel import Selector
from rapidfuzz import fuzz
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from whoswho import who


class PaperId(str):
    ...


class ArxivId(PaperId):
    ...


class S2Id(PaperId):
    ...


def _trim_version(arxiv_id: str) -> str:
    return re.sub(r"v\d+$", "", arxiv_id)


def are_same_title(title1: str, title2: str) -> bool:
    return fuzz.ratio(title1.lower(), title2.lower()) > 90


def are_same_author(author1: str, author2: str) -> bool:
    return cast(bool, who.match(author1, author2))


@dataclass
class S2Paper:
    id: str
    title: str
    authors: List[str]
    abstract: str
    year: int
    venue: Optional[str]
    url: str
    arxiv_id: Optional[str]
    arxiv_url: Optional[str]
    figure_urls: List[str]
    table_urls: List[str]


@dataclass
class S2SearchClient:
    delay_sec: Optional[int] = 1
    _cli: httpx.Client = field(
        default=httpx.Client(base_url="https://api.semanticscholar.org"),
        init=False,
    )
    _driver: WebDriver = field(init=False)
    _prev_req_time: Optional[float] = field(default=None, init=False)

    def __post_init__(self):
        o = Options()
        o.add_argument("--headless")

        ua = UserAgent()
        o.add_argument(f"user-agent={ua.chrome}")

        self._driver = webdriver.Chrome(ChromeDriverManager().install(), options=o)

    def _assure_deley(self):
        if self._prev_req_time is not None and self.delay_sec is not None:
            now = time()
            wait_secs = max(0.0, self.delay_sec - (now - self._prev_req_time))
            sleep(wait_secs)

    def search_exact(self, title: str, first_author: str) -> Optional[S2Id]:
        q = f"{title} {first_author}"
        query = {"q": q, "sort": "relevance"}
        params = urlencode(query)
        base_url = "https://www.semanticscholar.org"

        self._assure_deley()
        self._prev_req_time = time()
        self._driver.get(f"{base_url}/search?{params}")

        try:
            WebDriverWait(self._driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "result-page"))
            )
            found_paper_elems = self._driver.find_elements_by_xpath(
                "//div[contains(@class, 'cl-paper-row')]"
            )
        except (TimeoutException, NoSuchElementException):
            return

        for found_paper_elem in found_paper_elems:
            found_title = found_paper_elem.find_element_by_xpath("./a").text
            found_first_author = found_paper_elem.find_element_by_xpath(
                ".//span[@data-heap-id='heap_author_list_item']"
            ).text

            if are_same_title(title, found_title) and are_same_author(
                first_author, found_first_author
            ):
                url = found_paper_elem.find_element_by_xpath("./a").get_attribute(
                    "href"
                )
                s2id = url.split("/")[-1]
                return S2Id(s2id)

    def search_best(self, title: str, first_author: Optional[str]) -> Optional[S2Id]:
        q = f"{title} {first_author or ''}".strip()
        query = {"q": q, "sort": "relevance"}
        params = urlencode(query)
        base_url = "https://www.semanticscholar.org"

        self._assure_deley()
        self._prev_req_time = time()
        self._driver.get(f"{base_url}/search?{params}")

        try:
            WebDriverWait(self._driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "result-page"))
            )
            first_paper_elem = self._driver.find_element_by_xpath(
                "//div[contains(@class, 'cl-paper-row')]"
            )
        except (TimeoutException, NoSuchElementException):
            return

        url = first_paper_elem.find_element_by_xpath("./a").get_attribute("href")
        s2id = url.split("/")[-1]
        return S2Id(s2id)


@dataclass
class S2Client:
    """Semantic Scholar Client.

    Attributes
    ----------
    delay_sec : int
        Minimum request interval (the default is 3 because we can only request up to
        100 per five minute).
    """

    delay_sec: Optional[int] = 3
    _api_cli: httpx.Client = field(
        default=httpx.Client(base_url="https://api.semanticscholar.org"),
        init=False,
    )
    _page_cli: httpx.Client = field(default=httpx.Client(), init=False)
    _prev_req_time: Optional[float] = field(default=None, init=False)
    _search_cli: S2SearchClient = field(default=S2SearchClient(), init=False)

    def _assure_deley(self):
        if self._prev_req_time is not None and self.delay_sec is not None:
            now = time()
            wait_secs = max(0.0, self.delay_sec - (now - self._prev_req_time))
            sleep(wait_secs)

    def _fetch_figure_and_table_urls(self, s2url: str) -> Tuple[List[str], List[str]]:
        res = self._page_cli.get(s2url)
        res.raise_for_status()

        figures = []
        tables = []
        selector = Selector(res.content.decode())
        for img in selector.xpath("//li/a/figure/div/img"):
            url = img.attrib["src"]
            if "-Figure" in url:
                figures.append(url)
            elif "-Table" in url:
                tables.append(url)

        return figures, tables

    def _fetch(self, id: PaperId) -> Optional[S2Paper]:
        if isinstance(id, ArxivId):
            query = f"/v1/paper/arXiv:{id}"
        elif isinstance(id, S2Id):
            query = f"/v1/paper/{id}"
        else:
            raise NotImplementedError

        self._assure_deley()
        self._prev_req_time = time()

        res = self._api_cli.get(query)
        if res.status_code == httpx.codes.NOT_FOUND:
            return

        res.raise_for_status()

        data = res.json()
        figure_urls, table_urls = self._fetch_figure_and_table_urls(data["url"])
        arxiv_id = data["arxivId"]
        arxiv_url = f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else None

        return S2Paper(
            id=data["paperId"],
            title=data["title"],
            authors=[author["name"] for author in data["authors"]],
            abstract=data["abstract"],
            year=data["year"],
            venue=data["venue"],
            url=data["url"],
            arxiv_id=arxiv_id,
            arxiv_url=arxiv_url,
            figure_urls=figure_urls,
            table_urls=table_urls,
        )

    def _fetch_with_retry(self, id: PaperId) -> Optional[S2Paper]:
        try:
            return self._fetch(id)
        except:
            return self._fetch(id)

    def fetch_from_arxiv_id(self, arxiv_id: str) -> Optional[S2Paper]:
        arxiv_id = _trim_version(arxiv_id)
        return self._fetch_with_retry(ArxivId(arxiv_id))

    def fetch_from_s2_id(self, s2_id: str) -> Optional[S2Paper]:
        return self._fetch_with_retry(S2Id(s2_id))

    def search_exact(self, title: str, first_author: str) -> Optional[S2Paper]:
        s2id = self._search_cli.search_exact(title, first_author)
        if s2id is not None:
            return self.fetch_from_s2_id(s2id)

    def search_best(
        self, title: str, first_author: Optional[str] = None
    ) -> Optional[S2Paper]:
        s2id = self._search_cli.search_best(title, first_author)
        if s2id is not None:
            return self.fetch_from_s2_id(s2id)

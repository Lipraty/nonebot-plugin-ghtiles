import json
import re
import httpx
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup


def get_today() -> str:
    return datetime.now().strftime("%Y-%m-%d")

# only contributions html elements
async def get_homepage_html(gh_name: str, proxy: str = "https://github.com") -> str:
    url = f"{proxy}/{gh_name}?action=show&controller=profiles&tab=contributions&user_id={gh_name}"
    headers = {
        "X-Requested-With": "XMLHttpRequest"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.text


async def check_contributions(gh_html: str) -> bool:
    return re.compile(r"\'s activity is private\<\/h2\>").search(gh_html) is None


async def get_today_contributions(gh_html: str) -> int:
    soup = BeautifulSoup(gh_html, "html.parser")
    contributions = 0
    if soup.tbody is None:
        return contributions
    tt = soup.tbody("tool-tip")
    today_index = next((index for index, td in enumerate(soup.tbody("td", class_="ContributionCalendar-day")) if td.get('data-date') == get_today()), None)
    if today_index is not None:
        search = re.compile(r"(\d+|No) contribution").search(tt[today_index].text)
        if search:
            if search.group(1) == "No":
                return contributions
            contributions = int(search.group(1))
    return contributions

class AutoSave:
    def __init__(self, fileProxy: Path, proxy: dict = None, initial_data: dict = None): # type: ignore
        self._fileProxy = fileProxy
        if proxy is None:
            if fileProxy.exists():
                load_by_file = json.loads(fileProxy.read_text())
                self._proxy = load_by_file if load_by_file else initial_data or {}
            else:
                self._proxy = initial_data or {}
        else:
            self._proxy = proxy
        self._save()

    def _save(self):
        self._fileProxy.write_text(json.dumps(self._proxy, ensure_ascii=False))

    def __getitem__(self, name):
        return self._proxy[name]

    def __setitem__(self, name: str, value):
        self._proxy[name] = value
        self._save()

    def __delitem__(self, name: str):
        del self._proxy[name]
        self._save()

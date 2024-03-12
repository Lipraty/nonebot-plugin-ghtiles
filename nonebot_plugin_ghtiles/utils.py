import json
import re
import httpx
from datetime import datetime
from pathlib import Path


def get_today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


async def get_homepage_html(gh_name: str, proxy: str = "https://github.com") -> str:
    url = f"{proxy}/{gh_name}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


async def check_contributions(gh_name: str, gh_html: str) -> bool:
    return re.compile(r"\'s activity is private\<\/h2\>").search(gh_html) is None


async def get_today_contributions(gh_name: str, gh_html: str):
    match = re.compile(
        r'data-date="' + get_today() + r".*?(\d+|No) contributions"
    ).search(gh_html)
    if match:
        contributions = match.group(1)
        if contributions == "No":
            return 0
        else:
            return int(contributions)
    else:
        return 0


class AutoSave:
    def __init__(self, fileProxy: Path, proxy = None):
        if proxy is None:
            if fileProxy.exists():
                self._proxy = json.loads(fileProxy.read_text())
            else:
                self._proxy = {}
        else:
            self._proxy = proxy
        self._fileProxy = fileProxy

    def _save(self):
        self._fileProxy.write_text(json.dumps(self._proxy, ensure_ascii=False))
    
    def __getattr__(self, name):
        return getattr(self._proxy, name)
    
    def __getitem__(self, name):
        return self._proxy[name]
    
    def __setattr__(self, __name: str, __value):
        if __name == "_proxy" or __name == "_fileProxy":
            super().__setattr__("_proxy", __name)
        else:
            setattr(self._proxy, __name, __value)
            self._save()
    
    def __setitem__(self, __name: str, __value):
        if __name == "_proxy":
            super().__setattr__("_proxy", __name)
        else:
            self._proxy[__name] = __value
            self._save()
    
    def __delitem__(self, __name: str):
        del self._proxy[__name]
        self._save()

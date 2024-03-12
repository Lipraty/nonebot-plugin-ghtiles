
from typing_extensions import Annotated
from pydantic import BaseModel, Field, HttpUrl


class Config(BaseModel):
    ght_proxy: Annotated[str, HttpUrl] = Field("https://github.com", title="GitHub Proxy", description="GitHub 代理地址")

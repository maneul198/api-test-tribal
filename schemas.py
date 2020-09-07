from enum import Enum
from typing import List, Any
from pydantic import BaseModel, constr


class MediaTypeEnum(str, Enum):
    movie = 'movie'
    song = 'song'
    person = 'person'
    show = 'show'


class Filter(BaseModel):
    term: str = None
    country: constr(min_length=2, max_length=2) = None
    id: int = None
    tvrage: int = None
    thetvdb: int = None
    imdb: str = None


class Query(BaseModel):
    type: MediaTypeEnum = MediaTypeEnum.movie
    filter: Filter


class SearchResults(BaseModel):
    source: str
    results: List[Any] = []
    count: int = 0

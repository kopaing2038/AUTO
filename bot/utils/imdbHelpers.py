import asyncio
import re
import time
from typing import List
from urllib.parse import quote, urljoin

from imdbpie import Imdb
from trans import trans

from ..config import Config
from .tools import run_in_thread

from googletrans import Translator
import logging

log = logging.getLogger(__name__)

translator = Translator()

def list_to_str(k):
    if not k:
        return "N/A"
    elif len(k) == 1:
        return str(k[0])
    elif Config.MAX_LIST_ELM:
        k = k[: int(Config.MAX_LIST_ELM)]
        return " ".join(f"{elem}, " for elem in k)
    else:
        return " ".join(f"{elem}, " for elem in k)


_MAX_CACHE = 3600
_PREFERRED_QUALITY = 320
_PREFERRED_QUALITY = 320


_REGEX_POSTER = re.compile(
    r"https:\/\/m.media-amazon.com\/images\/M\/(?P<posterID>[a-zA-Z0-9_\-@]*)\._V1_(?P<aspectRatio>.*?)\.(?P<ext>\w+)",
    re.IGNORECASE,
)

_DEFAULT_TEMPLATE = """
○ **Title**: `{title}`
○ **Released on**: `{release_date}`
○ **Genres**: `{genres}`
○ **Rating**: `{rating} ({rating_count} votes)`
"""


class IMDB(Imdb):
    def __init__(self, locale=None, exclude_episodes=False, session=None):
        self.titleCache = {}
        super().__init__(locale, exclude_episodes, session)

    def _get_title_release_date(self, imdb_id):
        try:
            releases_data = self.get_title_releases(imdb_id=imdb_id)
        except LookupError:
            return None
        else:
            return releases_data["releases"][0]["date"]

    async def _getInfo(self, imdb_id) -> dict:
        _tasks = [
            run_in_thread(self.get_title)(imdb_id),
            run_in_thread(self.get_title_auxiliary)(imdb_id=imdb_id),
            run_in_thread(self._get_title_release_date)(imdb_id=imdb_id),
        ]
        base_title_data, title_aux_data, release_date = await asyncio.gather(*_tasks)
        title = base_title_data["base"]["title"]
        year = base_title_data["base"].get("year")
        try:
            rating = float(base_title_data["ratings"]["rating"])
        except KeyError:
            rating = None
        type_ = base_title_data["base"]["titleType"].capitalize()

        try:
            rating_count = base_title_data["ratings"]["ratingCount"]
        except KeyError:
            rating_count = 0

        try:
            plot_outline = translator.translate(base_title_data["plot"]["outline"]["text"], src='en', dest='my').text
        except KeyError:
            plot_outline = None

        try:
            genres = tuple(g.capitalize() for g in title_aux_data.get("genres", []))
        except TypeError:
            genres = ()

        try:
            certification = title_aux_data["certificate"]["certificate"]
        except TypeError:
            certification = None
        stars = [i["name"] for i in title_aux_data["principals"]]
        try:
            image = title_aux_data["image"]["url"]
        except KeyError:
            image = None
        try:
            runtime = title_aux_data["runningTimes"][0]["timeMinutes"]
        except (KeyError, IndexError):
            runtime = None
        try:
            season = title_aux_data["season"]
            episode = title_aux_data["episode"]
        except KeyError:
            season = None
            episode = None
        return dict(
            imdb_id=imdb_id,
            title=title,
            year=year,
            rating=rating,
            kind=type_,
            release_date=release_date,
            plot=plot_outline,
            votes=rating_count,
            genres=", #".join(genres).strip().rstrip(", #"),
            certification=certification,
            poster=image,
            cast=", #".join(stars).strip().rstrip(", #"),
            runtime=runtime,
            seasons=season,
            episode=episode,
            localized_title=title,
            url=f"https://www.imdb.com/title/{imdb_id}",
        )

    def search_for_title(self, title):
        cleaned_query = trans(title)
        query_encoded = quote(cleaned_query)
        first_alphanum_char = self._query_first_alpha_num(cleaned_query)
        path = "/suggestion/{0}/{1}.json".format(first_alphanum_char, query_encoded)
        url = urljoin("https://v3.sg.media-imdb.com", path)
        search_results = self._get(url=url, query=query_encoded)
        results = []
        for result in search_results.get("d", ()):
            if not result["id"].startswith("tt"):
                # ignore non-title results
                continue
            result_item = {
                "title": result["l"],
                "year": result.get("y"),
                "imdb_id": result["id"],
                "type": result.get("qid", "movie"),
                "image": result.get("i", {}).get("imageUrl", ""),
            }
            results.append(result_item)
        return results

    async def searchMovie(self, title: str) -> List[dict]:
        if title.startswith("tt"):
            res = await self.getInfo(title)
            return [res]
        res = await run_in_thread(self.search_for_title)(title.lower())
        return res

    async def getInfo(self, imdbID: str, force: bool = False) -> dict:
        if imdbID in self.titleCache:
            info = self.titleCache[imdbID]
            if time.time() - info["time"] > _MAX_CACHE:
                force = True
        else:
            force = True

        if force:
            info = await self._getInfo(imdbID)
            if info:
                self.titleCache[imdbID] = {"time": time.time(), "data": info}
        return self.titleCache.get(imdbID, {}).get("data")  # type: ignore

    def parsePoster(self, posterURL: str, quality: int = _PREFERRED_QUALITY) -> str:
        _res = _REGEX_POSTER.search(posterURL)
        if not _res:
            return ""
        return f'https://m.media-amazon.com/images/M/{_res.group("posterID")}._V1_UX{quality}.{_res.group("ext")}'

    def parseTemplate(self, template: str, data: dict) -> str:
        try:
            return template.format(**data)
        except Exception:
            return _DEFAULT_TEMPLATE.format(**data)

    def parsePoster(self, posterURL: str, quality: int = _PREFERRED_QUALITY) -> str:
        _res = _REGEX_POSTER.search(posterURL)
        if not _res:
            return ""

        image_url = f'https://m.media-amazon.com/images/M/{_res.group("posterID")}._V1_UX{quality}.{_res.group("ext")}'
        aspect_ratio = self._get_image_aspect_ratio(image_url)
        if aspect_ratio != 16 / 9:
            return ""

        return image_url

    def _get_image_aspect_ratio(self, image_url: str) -> float:
        response = requests.get(image_url, stream=True)
        response.raw.decode_content = True

        with Image.open(response.raw) as image:
            width, height = image.size
            aspect_ratio = width / height

        return aspect_ratio



IMDb = IMDB()


async def get_poster(
    query: str, bulk: bool = False, imdb_id: int = False, file: str = None  # type: ignore
) -> dict:
    if not imdb_id:
        query = (query.strip()).lower()
        title = query
        year = re.findall(r"[1-2]\d{3}$", query, re.IGNORECASE)
        if year:
            year = list_to_str(year[:1])
            title = (query.replace(year, "")).strip()
        elif file is not None:
            year = re.findall(r"[1-2]\d{3}", file, re.IGNORECASE)
            if year:
                year = list_to_str(year[:1])
        else:
            year = None
        movie_id = await IMDb.searchMovie(title.lower())
        if not movie_id:
            return None  # type: ignore
        if year:
            filtered = list(filter(lambda k: str(k.get("year")) == str(year), movie_id))
            if not filtered:
                filtered = movie_id
        else:
            filtered = movie_id
        movie_id = filtered
        if not movie_id:
            movie_id = filtered
        if bulk:
            return movie_id  # type: ignore
        movie_id = movie_id[0]["imdb_id"]
    else:
        movie_id = query
    if not movie_id.startswith("tt"):
        movie_id = f"tt{movie_id}"

    movie = await IMDb.getInfo(movie_id)
    if not movie:
        return None
    return movie

async def get_photo(query: str, file: str = None) -> dict:
    try:
        query = (query.strip()).lower()
        title = query
        movie_id = await IMDb.searchMovie(title.lower())
        movie = await IMDb.getInfo(movie_id[0]["imdb_id"])

        title = movie.get("title", "N/A")
        year = movie.get("year", "N/A")
        rating = movie.get("rating", "N/A")
        runtime = movie.get("runtimes", ["N/A"])[0]
        summary = movie.get("plot", ["N/A"])[0].split("::")[0]
        photo_url = movie.get("cover url", "N/A")

        return {
            "title": title,
            "year": year,
            "rating": rating,
            "runtime": runtime,
            "summary": summary,
            "photo": photo_url
        }
    except Exception as e:
        log.exception(e)
        return {}


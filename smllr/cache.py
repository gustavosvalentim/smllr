import logging

from datetime import datetime
from django.conf import settings
from django.utils.timezone import make_aware
from smllr.shorturls.models import ShortURL
from redis import Redis
from redis.commands.search.field import TextField, NumericField
from redis.commands.search.query import Query
from redis.commands.search.index_definition import IndexDefinition
from redis.exceptions import RedisError
from typing import TypedDict

from smllr.users.models import User


logger = logging.getLogger(__name__)


class RedisConnectionConfiguration(TypedDict):
    host: str
    port: int
    username: str | None
    password: str | None


class RedisConnectionFactory:
    current_connection: Redis | None = None

    def _create_connection(config: RedisConnectionConfiguration) -> Redis:
        try:
            conn = Redis(
                host=config["host"],
                port=config["port"],
                username=config.get("username"),
                password=config.get("password"),
            )
            return conn
        except Exception as err:
            logger.error("Error creating connection with Redis", err, exc_info=True)
            raise Exception(f"Error connecting to Redis at {config['host']}:{config['port']}")

    @staticmethod
    def get() -> Redis:
        if RedisConnectionFactory.current_connection is None:
            RedisConnectionFactory.current_connection = RedisConnectionFactory._create_connection(settings.REDIS)
        return RedisConnectionFactory.current_connection


class ShortURLCache:
    index_name = "shorturl"

    def __init__(self, connection: Redis):
        self.connection = connection
        self.create_index()

    def create_index(self):
        schema = (
            NumericField("url_id"),
            TextField("code"),
            TextField("url"),
            NumericField("created_at"),
            NumericField("user_id"),
        )
        try:
            self.connection.ft(self.index_name).create_index(
                schema,
                definition=IndexDefinition(prefix=f"{self.index_name}:"),
            )
        except RedisError:
            logger.debug("ShortURL index definition already exists")

    def set(self, code: str, url: str, created_at: datetime, user_id: int):
        self.connection.hset(f"shorturl:{code}", mapping={
            "code": code,
            "url": url,
            "created_at": created_at.timestamp(),
            "user_id": user_id,
        })

    def get(self, code: str) -> ShortURL | None:
        query = Query(f"@code:{code}")
        res = self.connection.ft(self.index_name).search(query)

        if len(res.docs) == 0:
            return None

        doc = res.docs[0]
        created_at = datetime.fromtimestamp(float(doc.created_at))

        short_url = ShortURL(
            user = User(pk=doc.user_id),
            destination_url = doc.url,
            short_code = doc.code,
            created_at = make_aware(created_at),
        )

        return short_url 


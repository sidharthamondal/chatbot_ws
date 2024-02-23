import redis
from redis.commands.search.query import Query

from Chatserver.redisCache import QnACache
dynamic_cache = QnACache()

print(dynamic_cache.get_top_questions(str(b'Alizin'),1))
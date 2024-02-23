# Import necessary libraries and modules
import redis  # Redis is used as a data store
from redis.commands.search.field import TagField, VectorField  # Redis search field types
from redis.commands.search.indexDefinition import IndexDefinition, IndexType  # Redis index definitions
from redis.commands.search.query import Query  # Redis search queries
from sentence_transformers import SentenceTransformer  # Sentence embeddings library
import numpy as np  # NumPy for numerical operations
import datetime
from . import envVars


# Define a class for Q&A caching using Redis and SentenceTransformer
class QnACache:
    def __init__(self, host=envVars.redis, port=6379, vector_dimensions=384):
        # Initialize the Redis connection and set configuration parameters
        self.redis = redis.Redis(host=host, port=port, db=0)
        self.INDEX_NAME = "qnaCache"  # Name of the Redis search index
        self.DOC_PREFIX = "qna:"  # Prefix for Redis document keys
        self.VECTOR_DIMENSIONS = vector_dimensions  # Dimensions for sentence vectorization
        self.sentence_transformer = SentenceTransformer("all-MiniLM-L6-v2")  # Load SentenceTransformer model

        # Check if the index exists; if not, create it
        if not self.index_exists():
            self.create_index()

    def index_exists(self):
        # Check if the Redis search index exists
        try:
            self.redis.ft(self.INDEX_NAME).info()
            return True
        except redis.exceptions.ResponseError:
            return False

    def create_index(self):
        # Define the schema and index definition for the Redis search index
        schema = (
            TagField("tag"),  # Tag field for unique identifiers
            VectorField("vector", "FLAT", {"TYPE": "FLOAT32", "DIM": self.VECTOR_DIMENSIONS, "DISTANCE_METRIC": "COSINE"})
        )
        definition = IndexDefinition(prefix=[self.DOC_PREFIX], index_type=IndexType.HASH)

        # Create the Redis search index
        self.redis.ft(self.INDEX_NAME).create_index(fields=schema, definition=definition)

    def store_qna(self, agentid, organizationid, entity, question, answer):
        # Prepare the Q&A object with relevant metadata
        qna_object = {
            "tag": str(agentid) + "_" + str(organizationid) + "_" + entity,
            "entity": entity,
            "organizationId": organizationid,
            "agentid": agentid,
            "question": question,
            "answer": answer,
            "score":0,
            "lastUsed":0
        }

        # Get the next available ID
        obj_id = self.get_next_id()

        # Define the Redis key for the Q&A document
        key = f"{self.DOC_PREFIX}{obj_id}"

        # Vectorize the question using SentenceTransformer
        question_vector = self.vectorize_sentence(question)

        # Store the Q&A data in Redis
        pipe = self.redis.pipeline()
        pipe.hset(key, mapping=qna_object)
        pipe.zadd(self.INDEX_NAME, {key: obj_id})
        pipe.hset(key, "vector", question_vector.tobytes())
        pipe.execute()

    def vectorize_sentence(self, sentence):
        # Vectorize a sentence using SentenceTransformer and convert it to NumPy array
        embeddings = self.sentence_transformer.encode(sentence, convert_to_numpy=True)
        return embeddings.astype(np.float32)

    def get_next_id(self):
        # Increment and return the auto-increment ID for document keys
        return self.redis.incr("auto_increment_id")

    # def search_qna(self, query, query_params):
    #     # Perform a Redis search based on the given query and query parameters
    #     return self.redis.ft(self.INDEX_NAME).search(query, query_params).docs
    def update_score_and_timestamp(self, key):
        # Update the score parameter in the corresponding hash by 1
        self.redis.hincrby(key, "score", 1)

        # Update the timestamp field in the hash to the current UTC time
        timestamp_field = "last_updated"
        utc_now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
        timestamp = utc_now.timestamp()
        self.redis.hset(key, timestamp_field, int(timestamp))

        # Update the sorted set with the combined score and timestamp
        score = self.redis.hget(key, "score")
        combined_score_timestamp = float(score) + timestamp
        entity = self.redis.hget(key, "entity")
        sorted_set_key = "top_questions_"+str(entity)
        self.redis.zadd(sorted_set_key, {key: combined_score_timestamp})

    def get_top_questions(self, entity, count=3):
        # Retrieve the top 3 questions for the specified entity
        sorted_set_key = "top_questions_"+entity
        print(sorted_set_key)
        questions = self.redis.zrevrangebyscore(sorted_set_key, '+inf', '-inf', start=0, num=count, withscores=True)
        return questions

    def search_qna(self, query, query_params):
        # Perform a Redis search based on the given query and query parameters
        search_results = self.redis.ft(self.INDEX_NAME).search(query, query_params).docs
        try:
            key = search_results[0]['id']
            self.update_score_and_timestamp(key)
            # Update the score parameter in each search result
            return search_results
        except Exception as e:
            print(e)
            return None    




    def log_access(self, hash_key):
        # Log the access frequency for a given hash key
        self.redis.zincrby("score", 1, hash_key)


# Example usage:
# if __name__ == "__main__":
#     qna_cache = QnACache()

#     agentid = ""
#     organisationid = "994cd27adfcb5e14807c9cfb3901a0b9"
#     entity = "74fa6e1d5c395c6eaadb27bfae78fe3a"
#     question = "what is it used for ?"
#     entity = "alizin"

#     # Store a Q&A pair
#     # qna_cache.store_qna(agentid, entity, question, answer)
#     tag =str(agentid)+"_"+ str(organisationid)+"_"+ entity
#     # Example search query
#     query = (
#         Query(f"@vector:[VECTOR_RANGE $radius $vec]=>{{ $YIELD_DISTANCE_AS: score }}")
#         .sort_by("score")
#         .return_fields("entity", "agentid", "score","answer")
#         .paging(0, 1)
#         .dialect(2)
#     )
#     # Vectorize the query using SentenceTransformer
#     query_vector = qna_cache.vectorize_sentence(question)

#     # Find all vectors within a certain radius of the query vector
#     query_params = {
#         "radius": 10,
#         "vec": query_vector.tobytes()
#     }
    
#     search_result = qna_cache.search_qna(query, query_params)
#     value = search_result[0]['id']
#     qna_cache.log_access(str(value))

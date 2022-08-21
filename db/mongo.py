import os
from pymongo import MongoClient

MONGO_CONNECTION_STRING = os.environ.get(
    "MONGO_CONNECTION_STRING", default="mongodb://localhost:27017/"
)
MONGO_COLLECTION_OPENCOMMENTS = os.environ.get("MONGO_DB_COLLECTION", default="test-opencomments")
MONGO_COLLECTION_AWS_QUESTIONS = os.environ.get("MONGO_COLLECTION_AWSQUESTIONS", default="test-awsquestions")

client_opencomments = MongoClient(MONGO_CONNECTION_STRING)
db_opencomments = client_opencomments[MONGO_COLLECTION_OPENCOMMENTS]

client_aws_questions = MongoClient(MONGO_CONNECTION_STRING)
db_aws_questions = client_opencomments[MONGO_COLLECTION_AWS_QUESTIONS]
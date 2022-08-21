from bson.objectid import ObjectId
from flask import Blueprint, request
import os

from db.mongo import db_aws_questions

AWS_QUESTIONS_SECRET = os.environ.get("AWS_QUESTIONS_SECRET")
questions = db_aws_questions.questions
blp_aws_exam = Blueprint("aws_exam", __name__)


@blp_aws_exam.route("/getRandomQuestion", methods=["POST"])
def get_randon_question():
    '''
    return:
    {
        data: {
            question... },
        questionsCount: number
    }
    '''
    # payload = request.get_json()
    q = questions.aggregate([{"$sample": {"size": 1}}]).next()
    q["_id"] = str(q["_id"])
    count = questions.count_documents({})
    return {"data": q, "questionsCount": count}


@blp_aws_exam.route("/addNewQuestion", methods=["POST"])
def put_question():
    print(AWS_QUESTIONS_SECRET, "---------")
    payload = request.get_json()
    if str(payload["secret"]) != AWS_QUESTIONS_SECRET:
        print({"error": "Invalid secret", "payload": payload})
        return {"error": "Invalid secret"}

    question_data = {}
    question_data["question"] = payload["question"]
    question_data["answers"] = payload["answers"]

    r = questions.insert_one(question_data)
    print(123, r)

    return {"status": "success"}

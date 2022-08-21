import requests

from flask import request, Flask, Blueprint, jsonify
from flask_cors import CORS
from urllib.parse import urlparse

from services import aws_exam, opencomments

app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"


def getAws(query):
    comments = []

    def comments_append(author, comment, date):
        comments.append({"author": author, "comment": comment, "date": date})

    def getRequstData(url, payload):
        res = requests.post(url, json=payload)
        res = res.json()
        return res

    def getTagsPageData(query):
        url = "https://repost.aws/api/v1/webClient/getTagsPageData"
        payload = {
            "maxResults": 1,
            "pagingTokenRange": 5,
            "query": query,
        }
        return getRequstData(url, payload)

    def listQuestions(tag_id):
        url = "https://repost.aws/api/v1/webClient/listQuestions"
        payload = {
            "maxResults": 5,
            "pagingTokenRange": 5,
            "tagId": tag_id,
            "view": "all",
        }
        return getRequstData(url, payload)

    def getQuestionData(question_id):
        url = "https://repost.aws/api/v1/webClient/getQuestionData"
        payload = {
            "questionId": question_id,
        }
        return getRequstData(url, payload)

    res = getTagsPageData(query)
    tag_id = res["data"]["tags"][0]["tagId"]
    res = listQuestions(tag_id)

    questions = res["data"]["questions"]
    for q in questions:
        question_id = q["questionId"]

        q = getQuestionData(question_id)["data"]["question"]
        title = q["title"]
        body = q["body"]
        date = q["updatedAt"]
        author = q["author"]["displayName"]

        comment = "<b>" + title + "</b></br>" + body
        comments_append(author, comment, date)

        q_answers = q.get("answers", [])

        for a in q_answers[:-10]:
            author = a["author"]["displayName"]
            body = a["body"]
            date = a["updatedAt"]

            comment = body
            comments_append(author, comment, date)

            q_comments = a.get("comments", [])
            if q_comments:
                for a in q_comments[:-10]:
                    author = a["author"]["displayName"]
                    body = a["body"]
                    date = a["updatedAt"]
                    comment = body
                    comments_append(author, comment, date)

    comments.sort(key=lambda x: x["date"], reverse=False)
    return comments


@app.route("/aws/getTagQuestions", methods=["GET"])
def aws_handler():
    tag = request.args.get("tag")
    aws_comments = getAws(tag)
    return {"comments": aws_comments}


@app.route("/")
def hello_world():
    r = request.args
    return f"<p>Hello, World!{r}</p>"


@app.route("/api/v1", methods=["GET"])
def info_view():
    """List of routes for this API."""
    output = {
        "info": "GET /api/v1",
        "register": "POST /api/v1/accounts",
        "single profile detail": "GET /api/v1/accounts/<username>",
        "edit profile": "PUT /api/v1/accounts/<username>",
        "delete profile": "DELETE /api/v1/accounts/<username>",
        "login": "POST /api/v1/accounts/login",
        "logout": "GET /api/v1/accounts/logout",
        "user's tasks": "GET /api/v1/accounts/<username>/tasks",
        "create task": "POST /api/v1/accounts/<username>/tasks",
        "task detail": "GET /api/v1/accounts/<username>/tasks/<id>",
        "task update": "PUT /api/v1/accounts/<username>/tasks/<id>",
        "delete task": "DELETE /api/v1/accounts/<username>/tasks/<id>",
    }
    return jsonify(output)


app.register_blueprint(aws_exam.blp_aws_exam, url_prefix="/aws")
app.register_blueprint(opencomments.blp_open_comments, url_prefix="/comments")


@app.before_request
def before_request():
    # referrer = request.referrer + request.environ["REQUEST_URI"]
    # print(request.environ["REQUEST_URI"])
    # print(request.environ)
    pass


if __name__ == "__main__":
    app.run()

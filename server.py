import datetime
import os
import requests

from flask import request, Flask, Blueprint
from flask_cors import CORS
from urllib.parse import urlparse
from pymongo import MongoClient

app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"


MONGO_CONNECTION_STRING = os.environ.get(
    "MONGO_CONNECTION_STRING", default="mongodb://localhost:27017/"
)
MONGO_DB_COLLECTION = os.environ.get("MONGO_DB_COLLECTION", default="test-database")

client = MongoClient()
client = MongoClient(MONGO_CONNECTION_STRING)

db = client[MONGO_DB_COLLECTION]
pages = db.pages
domains = db["domains"]
comments = db["comments"]

v1 = Blueprint("version1", "version1")
v2 = Blueprint("version2", "version2")


def get_date():
    return datetime.datetime.utcnow()


def get_page_comments(page):
    return comments.find_one(
        {"page": page}, {"_id": 1, "comments": 1, "page": 1, "views": 1}
    )


def update_page_view_count(page):
    comments.update_one(
        {"page": page},
        {
            "$inc": {"views": 1},
        },
        upsert=True,
    )


def set_parrent_comment(page, parent_id, comment):
    comments_page = comments.find_one({"page": page})
    if comments_page:
        if tmp_comments := comments_page.get("comments"):
            for c in tmp_comments:
                if c["id"] == parent_id:
                    children = c.get("comments", [])
                    children.append(comment)
                    c["comments"] = children
                    comments.update_one(
                        {"page": page},
                        {"$set": {"comments": tmp_comments}},
                    )
                    return True
        else:
            return False
    else:
        return False


#      get_date().timestamp(),
def create_page_comment(comment, page=None, author=None, parent_id=None):
    comment_data = {
        "id": str(get_date().timestamp())[-5:],
        "author": author or "Anonymous",
        "comment": comment,
        "date": get_date(),
    }
    if parent_id:
        updated = set_parrent_comment(page, parent_id, comment_data)
        if updated:
            return True

    res = comments.update_one(
        {"page": page}, {"$push": {"comments": comment_data}}, upsert=True
    )

    return res


def create_url_domain(url):
    domain_data = {"url": url, "date": get_date()}
    return domains.insert_one(domain_data)


def create_comment(comment, author=None, parent_id=None):
    date = get_date()
    comment_data = {
        "id": date.timestamp(),
        "author": author or "Anonymous",
        "comment": comment,
        "date": date,
    }
    if parent_id:
        comment_data["parent_id"] = parent_id
    return comments.insert_one(comment_data)


def create_url_page(url, domain_id):
    page_data = {"url": url, "domain_id": domain_id, "date": get_date()}
    return pages.insert_one(page_data)


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


@app.route("/comments", methods=["GET", "POST"])
def comments_handler():

    comment_page = request.args.get("page")
    request_domain = request.referrer

    comment = None

    if request.method == "POST":
        comment_data = request.get_json()
        comment = comment_data.get("comment")
        if comment:
            author = comment_data.get("author") or "Anonymous"
            parent_id = comment_data.get("parentId")
            comment_id = create_page_comment(comment, comment_page, author, parent_id)
            print("created comment", comment_id)
    elif request.method == "GET":
        update_page_view_count(comment_page)
        comments_data = []
        result = {"page": comment_page, "comments": comments_data}
        comments_fetched = get_page_comments(comment_page)
        if comments_fetched:
            comments_data = [
                comment for comment in comments_fetched.get("comments", [])
            ]
            result["page_views"] = comments_fetched.get("views", 0)
            result["comments"] = comments_data

        return result

    return {}


@app.route("/aws/getTagQuestions", methods=["GET"])
def aws_handler():
    tag = request.args.get("tag")
    aws_comments = getAws(tag)
    return {"comments": aws_comments}


@app.route("/")
@v2.route("/")
@v1.route("/")
def hello_world():
    r = request.args
    return f"<p>Hello, World!{r}</p>"


app.register_blueprint(v1, url_prefix="/v1")
app.register_blueprint(v2, url_prefix="/v2")


@app.before_request
def before_request():
    # referrer = request.referrer + request.environ["REQUEST_URI"]
    # print(request.environ["REQUEST_URI"])
    print(request.environ)


if __name__ == "__main__":
    app.run()

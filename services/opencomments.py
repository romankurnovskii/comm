import datetime
from flask import Blueprint, request

from db.mongo import db_opencomments

pages = db_opencomments.pages
domains = db_opencomments["domains"]
comments = db_opencomments["comments"]

blp_open_comments = Blueprint("open_comments", __name__)


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


@blp_open_comments.route("/", methods=["GET", "POST"])
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

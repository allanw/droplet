from bottle import route, redirect, request, abort, template, TEMPLATE_PATH
from dropbox import Dropbox
import os
import markdown

TEMPLATE_PATH.append('./droplet/templates')

dropbox = Dropbox()
dropbox.app_key = os.environ.get('DROPBOX_APP_KEY')
dropbox.app_secret = os.environ.get('DROPBOX_APP_SECRET')

def get_markdown():
    return markdown.Markdown(extensions=[
        "meta", "extra", "codehilite", "headerid(level=2)",
        "sane_lists",
    ])

def listing():
    files = dropbox.client.search("/", ".md")
    posts = []
    for f in files:
        src = dropbox.read_file(f['path'])
        mdown = get_markdown()
        html = mdown.convert(src)
        if "title" in mdown.Meta and "date" in mdown.Meta:
            posts.append({
                "path": f["path"][:-3],
                "title": mdown.Meta["title"][0],
                "date": mdown.Meta["date"][0],
                "html": html
            })
    return posts

@route('/')
@dropbox.connected
def index():
    return template('list', posts=listing())

@route('/<pagename>/')
@dropbox.connected
def page(pagename):
    post_listing = dropbox.client.search("/", ".md")
    url_listing = [p["path"] for p in post_listing]
    if "/" + pagename + ".md" not in url_listing:
        abort(404, "File not found")
    post_index = url_listing.index("/" + pagename + ".md")
    src = dropbox.read_file(pagename + ".md")
    mdown = get_markdown()
    html = mdown.convert(src)
    return template('post', body=html)

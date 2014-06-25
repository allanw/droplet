from bottle import route, redirect, request, abort, template, TEMPLATE_PATH
import os
import markdown
from dropbox.client import DropboxClient
from dropbox.session import DropboxSession, OAuthToken
from contextlib import closing

APP_KEY = os.environ['DROPBOX_APP_KEY']
APP_SECRET = os.environ['DROPBOX_APP_SECRET']

BLOG_POST_DIR = '/posts/'

TEMPLATE_PATH.append('./droplet/templates')

def read_file(fname):
    if os.path.exists(fname):
        with closing(open(fname)) as f:
            return f.read().decode('utf-8')
    else:
        return None

def get_client():
    sess = DropboxSession(APP_KEY, APP_SECRET, "dropbox")
    s_token = read_file('.s_token')
    s_secret = read_file('.s_secret')
    if s_token and s_secret:
        sess.set_token(s_token, s_secret)
    elif 'oauth_token' in request.query:
        r_token = read_file('.r_token')
        r_token_secret = read_file('.r_secret')
        s_token = sess.obtain_access_token(OAuthToken(r_token, r_token_secret))
        # Todo - uncomment these and set up redis
        # redis.set('s_token', s_token.key)
        # redis.set('s_secret', s_token.secret)
        with open('.s_token', 'w') as f:
            f.write(s_token.key)
        with open('.s_secret', 'w') as f:
            f.write(s_token.secret)
        os.remove('.r_token')
        os.remove('.r_secret')
    else:
        req_token = sess.obtain_request_token()
        with open(".r_token", "w") as f:
            f.write(req_token.key)
        with open(".r_secret", "w") as f:
            f.write(req_token.secret)
        url = sess.build_authorize_url(req_token, request.url)
        return redirect(url)
    return DropboxClient(sess)

@route('/foo')
def foo():
    client = get_client()
    files = client.search("/", ".md")
    for f in files:
        print f['path']
    return 'hello'


def get_markdown():
    return markdown.Markdown(extensions=[
        "meta", "extra", "codehilite", "headerid(level=2)",
        "sane_lists",
    ])

def listing():
    client = get_client()
    files = client.search(BLOG_POST_DIR, ".md")
    posts = []
    for f in files:
        src = client.get_file(f['path']).read()
        mdown = get_markdown()
        try:
            html = mdown.convert(src)
        except UnicodeDecodeError, e:
            print f['path'], e
        try:
            if "title" in mdown.Meta and "date" in mdown.Meta:
                posts.append({
                    "path": mdown.Meta["slug"][0],
                    "title": mdown.Meta["title"][0],
                    "date": mdown.Meta["date"][0],
                    "html": html
                })
        except AttributeError, e:
            print e
    return posts

@route('/')
def index():
    return template('list', posts=listing())

@route('/<pagename>')
@route('/<pagename>/')
def page(pagename):
    client = get_client()
    post_listing = client.search(BLOG_POST_DIR, ".md")
    url_listing = [p["path"] for p in post_listing]
    if BLOG_POST_DIR + pagename + ".md" not in url_listing:
        abort(404, "File not found")
    src = client.get_file(BLOG_POST_DIR + pagename + ".md").read()
    mdown = get_markdown()
    html = mdown.convert(src)
    return template('post', body=html)

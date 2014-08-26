from bottle import route, redirect, request, response, abort, template, TEMPLATE_PATH, static_file
import os
import markdown
from dropbox.client import DropboxClient
from dropbox.session import DropboxSession, OAuthToken
from contextlib import closing
import subprocess
import shutil
import StringIO
try:
    import redis
    redis_available = True
except ImportError:
    redis_available = False

APP_KEY = os.environ['DROPBOX_APP_KEY']
APP_SECRET = os.environ['DROPBOX_APP_SECRET']

BLOG_POST_DIR = '/posts/'

TEMPLATE_PATH.append('./droplet/templates')

REDISTOGO_URL = os.getenv('REDISTOGO_URL', None)
if REDISTOGO_URL == None:
    redis_url = '127.0.0.1:6379'
else:
    redis_url = REDISTOGO_URL

def read_file(fname):
    if os.path.exists(fname):
        with closing(open(fname)) as f:
            return f.read().decode('utf-8')
    else:
        return None

def get_client():
    sess = DropboxSession(APP_KEY, APP_SECRET, "dropbox")
    redis_client = redis.from_url(redis_url)
    s_token = redis_client.get('.s_token') if redis_available else read_file('.s_token')
    s_secret = redis_client.get('.s_secret') if redis_available else read_file('.s_secret')
    if s_token and s_secret:
        sess.set_token(s_token, s_secret)
    elif 'oauth_token' in request.query:
        r_token = redis_client.get('.r_token') if redis_available else read_file('.r_token')
        r_token_secret = redis_client.get('.r_secret') if redis_available else read_file('.r_secret')
        s_token = sess.obtain_access_token(OAuthToken(r_token, r_token_secret))
        if redis_available:
            redis_client.set('.s_token', s_token.key)
            redis_client.set('.s_secret', s_token.secret)
            redis_client.delete('.r_token')
            redis_client.delete('.r_secret')
        else:
            with open('.s_token', 'w') as f:
                f.write(s_token.key)
            with open('.s_secret', 'w') as f:
                f.write(s_token.secret)
            os.remove('.r_token')
            os.remove('.r_secret')
    else:
        req_token = sess.obtain_request_token()
        if redis_available:
            redis_client.set('.r_token', req_token.key)
            redis_client.set('.r_secret', req_token.secret)
        else:
            with open(".r_token", "w") as f:
                f.write(req_token.key)
            with open(".r_secret", "w") as f:
                f.write(req_token.secret)
        url = sess.build_authorize_url(req_token, request.url)
        return redirect(url)
    return DropboxClient(sess)

@route('/<filename:re:.*\.css>')
def serve_css(filename):
    return static_file(filename, root='droplet/static/css')

@route('/<filename:re:.*\.js>')
def serve_js(filename):
    return static_file(filename, root='droplet/static/js')

@route('/fonts/<filename:re:.*\.(eot|ttf|woff|svg)>')
def serve_fonts(filename):
    return static_file(filename, root='droplet/static/fonts')

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

@route('/cv')
@route('/cv.pdf')
def cv():
    client = get_client()
    cv_md = client.get_file(BLOG_POST_DIR + "cv.md").read()
    f = open('/tmp/cv_md.tmp', 'w')
    f.write(cv_md)
    f.close()
    options = ['pandoc', '/tmp/cv_md.tmp']
    options += ['--standalone']
    options += ['--section-divs']
    options += ['--template', 'droplet/templates/cv.html']
    options += ['--css', 'bootstrap.min.css']
    options += ['--css', 'style.css']
    options += ['--to', 'html5']
    p = subprocess.Popen(options, stdout=subprocess.PIPE)
    stdoutdata, stderrdata = p.communicate()
    f2 = open('/tmp/cv.html', 'w')
    f2.write(stdoutdata)
    f2.close()
    if request.path.endswith('.pdf'):
        options = ['wkhtmltopdf']
        options += ['--orientation', 'Portrait']
        options += ['--page-size', 'A4']
        options += ['--margin-top', '15']
        options += ['--margin-left', '15']
        options += ['--margin-right', '15']
        options += ['--margin-bottom', '15']
        options += ['/tmp/cv.html']
        # Use - to output PDF to stdout
        options += ['-']
        # Need to copy style.css and bootstrap.min.css to /tmp/
        # so they are in the same directory as cv.html
        shutil.copyfile('droplet/static/css/style.css', '/tmp/style.css')
        shutil.copyfile('droplet/static/css/bootstrap.min.css', '/tmp/bootstrap.min.css')
        p = subprocess.Popen(options, stdout=subprocess.PIPE)
        stdoutdata, stderrdata = p.communicate()
        cv_pdf = StringIO.StringIO()
        cv_pdf.write(stdoutdata)
        response.content_type = 'application/pdf'
        response.set_header('Content-Disposition', 'attachment; filename="report.pdf"')
        response.set_header('Content-Length', str(cv_pdf.len))
        return cv_pdf.getvalue()
    else:
        return stdoutdata
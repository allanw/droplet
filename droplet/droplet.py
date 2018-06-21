from bottle import route, redirect, request, response, abort, template, TEMPLATE_PATH, static_file
import os
import markdown
import dropbox
from contextlib import closing
import subprocess
import shutil
import StringIO
import cPickle as pickle
try:
    import redis
    redis_available = True
except ImportError:
    redis_available = False

APP_KEY = os.environ['DROPBOX_APP_KEY']
APP_SECRET = os.environ['DROPBOX_APP_SECRET']
DROPBOX_ACCESS_KEY = os.environ['DROPBOX_ACCESS_KEY']

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
    dbx = dropbox.Dropbox(DROPBOX_ACCESS_KEY)
    return dbx

@route('/<filename:re:.*\.css>')
def serve_css(filename):
    return static_file(filename, root='droplet/static/css')

@route('/<filename:re:.*\.js>')
def serve_js(filename):
    return static_file(filename, root='droplet/static/js')

@route('/fonts/<filename:re:.*\.(eot|ttf|woff|svg)>')
def serve_fonts(filename):
    return static_file(filename, root='droplet/static/fonts')

@route('/images/<filename:re:.*\.(jpg|png)>')
def serve_images(filename):
    return static_file(filename, root='droplet/static/images')

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
        except UnicodeDecodeError as e:
            print(f['path'], e)
        try:
            if "title" in mdown.Meta and "date" in mdown.Meta:
                posts.append({
                    "path": mdown.Meta["slug"][0],
                    "title": mdown.Meta["title"][0],
                    "date": mdown.Meta["date"][0],
                    "html": html
                })
        except AttributeError as e:
            print(e)
    return posts

@route('/')
def index():
    return template('index.tpl')

@route('/login')
def do_login():
    return 'hello'

@route('/blog')
@route('/blog/')
def blog():
    redis_client = redis.from_url(redis_url)
    l = redis_client.get("listing")
    if l:
        return template('list', posts=pickle.loads(l))
    else:
        posts = listing()
        redis_client.set("listing", pickle.dumps(posts))
        return template('list', posts=posts)

@route('/<pagename>')
@route('/<pagename>/')
def page(pagename):
    redis_client = redis.from_url(redis_url)
    p = redis_client.get(pagename)
    if p:
        return template('post', body=pickle.loads(p))
    else:
        client = get_client()
        post_listing = client.files_list_folder("/posts/*.md")
        url_listing = [p["path"] for p in post_listing]
        if BLOG_POST_DIR + pagename + ".md" not in url_listing:
            abort(404, "File not found")
        src = client.files_download(BLOG_POST_DIR + pagename + ".md").read()
        mdown = get_markdown()
        html = mdown.convert(src)
        redis_client.set(pagename, pickle.dumps(html))
        return template('post', body=html)

@route('/about')
@route('/about/')
def about():
    return template('about')

@route('/projects')
@route('/projects/')
def projects():
    return template('projects')

@route('/cv')
@route('/cv.pdf')
@route('/cv.txt')
def cv():
    client = get_client()
    metadata, res = client.files_download(BLOG_POST_DIR + "cv.md")
    cv_md = res.content
    f = open('/tmp/cv_md.tmp', 'w')
    f.write(cv_md)
    f.close()
    options = ['pandoc', '/tmp/cv_md.tmp']
    options += ['--standalone']
    options += ['--section-divs']
    options += ['--template', 'droplet/templates/cv.html']
    options += ['--css', 'cv_style.css']
    options += ['--from', 'markdown+yaml_metadata_block']
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
        # Need to copy style.css to /tmp/
        # so it is in the same directory as cv.html
        # I am using a slightly different cv_style CSS file (cv_style_pdf.css) for PDFs
        shutil.copyfile('droplet/static/css/cv_style_pdf.css', '/tmp/cv_style.css')
        p = subprocess.Popen(options, stdout=subprocess.PIPE)
        stdoutdata, stderrdata = p.communicate()
        cv_pdf = StringIO.StringIO()
        cv_pdf.write(stdoutdata)
        # foobar
        response.content_type = 'application/pdf'
        response.set_header('Content-Disposition', 'attachment; filename="cv.pdf"')
        response.set_header('Content-Length', str(cv_pdf.len)) 
        return cv_pdf.getvalue()
    elif request.path.endswith('.txt'):
        # plain text CV
        options = ['pandoc', '/tmp/cv_md.tmp']
        options += ['--filter', 'strip_headings_and_emphasis.py']
        options += ['--standalone']
        options += ['--section-divs']
        options += ['--from', 'markdown+yaml_metadata_block']
        options += ['--to', 'plain']
        p = subprocess.Popen(options, stdout=subprocess.PIPE)
        stdoutdata, stderrdata = p.communicate()
        response.content_type = 'text/plain'
        return stdoutdata
    else:
        return stdoutdata

from bottle import route, redirect, request, abort
from dropbox import Dropbox
import os

dropbox = Dropbox()
dropbox.app_key = os.environ.get('DROPBOX_APP_KEY')
dropbox.app_secret = os.environ.get('DROPBOX_APP_SECRET')

@route('/<pagename>/')
@dropbox.connected
def index(pagename):
    post_listing = listing()
    url_listing = [p["path"] for p in post_listing]
    if "/" + pagename + ".md" not in url_listing:
        abort(404, "File not found")
    post_index = url_listing.index("/" + pagename + ".md")
    src = dropbox.read_file(pagename + ".md")
    return 'hello world!'

def listing():
    return dropbox.client.search("/", ".md")

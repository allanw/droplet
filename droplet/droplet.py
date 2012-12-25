from bottle import route, run, redirect, request
from dropbox import Dropbox
import os

dropbox = Dropbox()
dropbox.app_key = os.environ.get('DROPBOX_APP_KEY')
dropbox.app_secret = os.environ.get('DROPBOX_APP_SECRET')
@route('/hello/')
@dropbox.connected
def index():
    return 'hello world'

def listing():
    return dropbox.client.search("/", ".md")

run(host='localhost', port=8090)

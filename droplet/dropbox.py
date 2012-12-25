from __future__ import absolute_import
from bottle import redirect, request
from dropbox.client import DropboxClient
from dropbox.session import DropboxSession, OAuthToken
from dropbox.rest import ErrorResponse
from contextlib import closing
import os
import redis

def read_file(fname):
    try:
        with open(fname, "r") as f:
            return f.read()
    except IOError:
        return None

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis = redis.from_url(redis_url)

class Dropbox(object):
    def __init__(self):
        self.client = None

    def read_file(self, fname):
        with closing(self.client.get_file(fname)) as r:
            return r.read().decode('utf-8')

    def connect(self, query):
        sess = DropboxSession(self.app_key, self.app_secret, "app_folder")
        s_token = redis.get('s_token') or read_file('.s_token')
        s_secret = redis.get('s_secret') or read_file('.s_secret')
        if s_token and s_secret:
            sess.set_token(s_token, s_secret)
        elif 'oauth_token' in request.query:
            r_token = read_file('.r_token')
            r_token_secret = read_file('.r_secret')
            s_token = sess.obtain_access_token(OAuthToken(
                        r_token, r_token_secret))
            redis.set('s_token', s_token.key)
            redis.set('s_secret', s_token.secret)
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
        self.client = DropboxClient(sess)

    def connected(self, fn):
        def wrapper(*args, **kwargs):
            if not self.client:
                self.connect(kwargs)
            try:
                return fn(*args, **kwargs)
            except ErrorResponse, e:
                print e #todo - finish this
        return wrapper

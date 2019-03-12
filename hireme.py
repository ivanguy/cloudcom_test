import requests, random
from functools import wraps
from flask import Flask, redirect, request, session

API_HOSTNAME = 'apiproxy.telphin.ru'
API_ADDR = f'https://{API_HOSTNAME}/api/ver1.0'
APP_ID = 'd844027694464e3fadfebad6daf2a6ce'
APP_SECRET = 'ef649710a28f4feb862f1c9dad1091b3'

app = Flask(__name__)
app.secret_key = b'ssssssssssssss'


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'client_id' not in session:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    return f'<p>{session}</p><form action="/login">\
                <button type="submit">Login with telfin</button>\
            </form>'


@app.route('/login')
def login():
    if 'client_id' in session:
        return redirect('/dashboard')
    redirect_uri = 'http://localhost:5000/authorized'

    return redirect(f'https://{API_HOSTNAME}/oauth/authorize?\
response_type=code&\
redirect_uri={redirect_uri}&\
client_id={APP_ID}&scope=all')


@app.route('/authorized')
def authorized():
    code = request.args.get('code')

    #get token with code
    payload = {
            'grant_type':'authorization_code',
            'code':code,
            'redirect_uri':f'http://localhost:5000/authorized',
            'client_id':APP_ID,
            'client_secret':APP_SECRET }
    r = requests.post(f'https://{API_HOSTNAME}/oauth/token',
            data = payload)
    session['token'] = r.json().get('access_token')

    headers = {'Authorization' : f'Bearer {session["token"]}'}
    r = requests.get(API_ADDR+'/user/', headers = headers).json()
    session['login'] = r.get('login')
    session['client_id'] = r.get('client_id')
    return redirect('/dashboard')


@app.route('/dashboard/')
@requires_auth
def dashboard():
    return f'<p>Hello {session["login"]} <a href="/logout">logout</a></p>\
            <a href="/extlist/">extlist</a>\
            <a href="/randomext/">randomext</a>'


@app.route('/logout')
def logout():
    session.pop('client_id')
    session.pop('login')
    session.pop('token')
    return f'Logged out!{session}'


@app.route('/extlist/')
@requires_auth
def extlist():
    headers = {'Authorization' : f'Bearer {session["token"]}'}
    r = requests.get(API_ADDR+f'/client/{session["client_id"]}/extension/', headers=headers)
    return str(r.json())

@app.route('/randomext/')
@requires_auth
def randomext():
    headers = {'Authorization' : f'Bearer {session["token"]}'}
    r = requests.get(API_ADDR+f'/client/{session["client_id"]}/extension/', headers=headers)
    exts = r.json()
    return str(exts[random.randrange(len(exts))])




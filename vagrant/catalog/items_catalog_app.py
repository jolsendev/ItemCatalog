from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from models.database_setup import Base, Catalog, CatalogItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///catalog_app.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())[
    'web']['client_id']


# READ
# "/" home shows categories and a list of the latest items worked on.
@app.route("/")
@app.route("/catalog")
def show_catalogs():
    catalogs = session.query(Catalog)
    items = {}  # session.query(CatalogItem).filter_by(catalog_id=catalogs.id)
    if 'username' not in login_session:
        return render_template('public_catalog_home.html', catalog_list=catalogs, catalog_items_list=items,login=False)
    else:
        return render_template("catalog_home.html", catalog_list=catalogs, catalog_items_list=items, login=True)


# "/catalog/<int:catalog_item>/items"  show a lost of items for a catagory item
@app.route("/catalog/<int:catalog_id>")
def show_catalog_items(catalog_id):
    catalogs = session.query(Catalog)
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    creator = getUserInfo(catalog.user_id)
    items = session.query(CatalogItem).filter_by(catalog_id=catalog_id)
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template("public_catalog_home_items.html", catalog_list=catalogs, catalog=catalog,
                               catalog_items_list=items, login=False)
    else:
        return render_template("catalog_home_items.html", catalog_list=catalogs, catalog=catalog,
                               catalog_items_list=items, login=True)


# "/catalog/<int:catalog_id>/<int:item_id>" - shows the description for a single item
@app.route("/catalog/<int:catalog_id>/item/<int:item_id>/description")
def show_item_description(catalog_id, item_id):
    return "Show catalog description for %s item %s" % (catalog_id, item_id)


# CREATE
# "/catalog/new" - new a category
@app.route("/catalog/new", methods=["POST", "GET"])
def create_catalog():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        new_catalog = Catalog(name=request.form["name"], description=request.form["description"])
        session.add(new_catalog)
        session.commit()
        flash('Catalog %s  Successfully Created' % (new_catalog.name))

        return redirect(url_for('show_catalog_items', catalog_id=new_catalog.id))
    return render_template("catalog_create.html")


# "/catalog/<int:catalog_item>/new" - new category item
@app.route("/catalog/<int:catalog_id>/new", methods=["GET", "POST"])
def create_catalog_item(catalog_id):
    if 'username' not in login_session:
        return redirect('/login')
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()

    if request.method == 'POST':
        try:

            print "my name: %s" % request.form['name']
            print "my description %s" % request.form['description']
            catalog_item = CatalogItem(
                name=request.form['name'], description=request.form['description'], catalog_id=catalog_id
            )
            session.add(catalog_item)
            session.commit()
            flash('Catalog Item %s  Successfully Created' % (catalog_item.name))
            return redirect(url_for('show_catalog_items', catalog_id=catalog_item.catalog_id))
        except SQLAlchemyError as e:
            print e.message

    return render_template("catalog_item_create.html", catalog=catalog)


# UPDATE
# "/catalog/<int:catalog_item>/edit" - edit a category
@app.route("/catalog/<int:catalog_id>/edit", methods=["GET", "POST"])
def edit_catalog(catalog_id):
    if 'username' not in login_session:
        return redirect('/login')
    edited_catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    if login_session['user_id'] != edited_catalog.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit catalog items to this catalog. Please create your own catalog in order to edit items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            edited_catalog.name = request.form['name']
        if request.form['description']:
            edited_catalog.description = request.form['description']
        session.add(edited_catalog)
        session.commit()
        flash('Catalog %s  Successfully Updated' % (edited_catalog.name))
        return redirect(url_for('show_catalog_items', catalog_id=edited_catalog.id))
    else:
        return render_template("catalog_edit.html", catalog=edited_catalog)


# "/catalog/<int:catalog_item>/<int:item_id>/edit" - edit a category
@app.route("/catalog/<int:catalog_id>/item/<int:item_id>/edit", methods=["POST", "GET"])
def edit_catalog_item(catalog_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    items = session.query(CatalogItem).filter_by(id=item_id)
    item = items.filter_by(catalog_id=catalog_id).one()
    if login_session['user_id'] != item.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit catalog items. Please create your own catalog in order to edit items.');}</script><body onload='myFunction()''>"
    if request.method == "POST":
        if request.form["name"]:
            item.name = request.form["name"]
        if request.form["description"]:
            item.description = request.form["description"]
        session.add(item)
        session.commit()
        flash('Catalog Item %s  Successfully Updated' % (item.name))
        return redirect(url_for('show_catalog_items', catalog_id=catalog_id))

    return render_template("catalog_item_edit.html", catalog_id=catalog_id, item=item)


# DELETE
# "/catalog/<int:catalog_item>/delete" - delete a category
@app.route("/catalog/<int:catalog_id>/delete", methods=["GET", "POST"])
def delete_catalog(catalog_id):
    if 'username' not in login_session:
        return redirect('/login')
    item_to_delete = session.query(Catalog).filter_by(id=catalog_id).one()
    if login_session['user_id'] != item_to_delete.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete this catalog. Please create your" \
               " own catalog in order to delete items.');}</script><body onload='myFunction()''>"
    if request.method == "POST":
        no = request.form.get('No', None)
        if no != None:
            return redirect(url_for('show_catalog_items', catalog_id=catalog_id))
        else:
            session.query(Catalog).filter_by(id=catalog_id).delete()
            session.commit()
            session.query(CatalogItem).filter_by(catalog_id=catalog_id).delete()
            flash('Catalog %s Successfully Deleted' % (item_to_delete.name))
            return redirect(url_for('show_catalogs'))
    else:
        return render_template("catalog_delete.html", catalog=item_to_delete)


# "/catalog/<int:catalog_item>/<int:item_id>/delete" - delete a category
@app.route("/catalog/<int:catalog_id>/item/<int:item_id>/delete", methods=["GET", "POST"])
def delete_catalog_item(catalog_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    items = session.query(CatalogItem).filter_by(id=item_id)
    item = items.filter_by(catalog_id=catalog_id).one()
    if login_session['user_id'] != item.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete this catalog. Please create your" \
               " own catalog in order to delete items.');}</script><body onload='myFunction()''>"
    if request.method == "POST":
        no = request.form.get('No', None)
        if no != None:
            return redirect(url_for('show_catalog_items', catalog_id=catalog_id))

        else:
            items.filter_by(catalog_id=catalog_id).delete()
            session.commit()
            flash('Catalog Item %s Successfully Deleted' % (item.name))
            return redirect(url_for('show_catalog_items', catalog_id=catalog_id))

    else:
        return render_template("catalog_item_delete.html", item=item, catalog_id=catalog_id)


# LOGIN
# "/catalog/login"
@app.route("/catalog/login")
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    # return "The currect state is %s "%state
    return render_template("login.html", STATE=state, login=None)


# "/catalog/gconnect"
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token.get('sub', None)
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token', None)
    stored_gplus_id = login_session.get('gplus_id', None)
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
        'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('show_catalogs'))
    else:
        flash("You were not logged in")
        return redirect(url_for('show_catalogs'))


@app.route('/catalog/<int:catalog_id>/JSON')
def catalog_items_json(catalog_id):
    catalogItems = session.query(CatalogItem).filter_by(catalog_id=catalog_id).all()
    return jsonify(MenuItems=[i.serialize for i in catalogItems])


@app.route('/catalog/JSON')
def catalogs_json():
    catalogs = session.query(Catalog).all()
    return jsonify(MenuItems=[i.serialize for i in catalogs])


@app.route('/catalog/<int:catalog_id>/item/<int:item_id>/JSON')
def catalog_item_json(catalog_id, item_id):
    catalogs = session.query(CatalogItem).filter_by(id=item_id)
    catlog_item = catalogs.filter_by(catalog_id=catalog_id)
    return jsonify(MenuItems=[i.serialize for i in catlog_item])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

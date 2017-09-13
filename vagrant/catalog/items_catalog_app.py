from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
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


# READ
# "/" home shows categories and a list of the latest items worked on.
@app.route("/")
@app.route("/catalog")
def show_catalogs():
    catalogs = session.query(Catalog)
    items = {}#session.query(CatalogItem).filter_by(catalog_id=catalogs.id)
    return render_template("catalog_home.html", catalog_list=catalogs, catalog_items_list=items)


# "/catalog/<int:catalog_item>/items"  show a lost of items for a catagory item
@app.route("/catalog/<int:catalog_item>")
def show_catalog_items(catalog_item):
    catalogs = session.query(Catalog)
    items = session.query(CatalogItem).filter_by(catalog_id=catalog_item)
    return render_template("catalog_home_items.html", catalog_list=catalogs, catalog_items_list=items)


# "/catalog/<int:catalog_id>/<int:item_id>" - shows the description for a single item
@app.route("/catalog/<int:catalog_id>/<int:item_id>/description")
def show_item_description(catalog_id, item_id):
    return "Show catalog description for %s item %s" % (catalog_id, item_id)


# CREATE
# "/catalog/new" - new a category
@app.route("/catalog/new", methods=["POST", "GET"])
def create_catalog():
    # if 'username' not in login_session:
    #     return redirect('/login')
    # restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    # if login_session['user_id'] != restaurant.user_id:
    #     return "<script>function myFunction() {alert('You are not authorized to add menu items to this restaurant. Please create your own restaurant in order to add items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        new_catalog = Catalog(name=request.form["name"])
        session.add(new_catalog)
        session.commit()
        return redirect(url_for('show_catalogs'))
    #     if request.method == 'POST':
    #         newItem = MenuItem(name=request.form['name'], description=request.form['description'], price=request.form[
    #                            'price'], course=request.form['course'], restaurant_id=restaurant_id, user_id=restaurant.user_id)
    #         session.add(newItem)
    #         session.commit()
    #         flash('New Menu %s Item Successfully Created' % (newItem.name))
    #         return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    # else:
    #     return render_template('newmenuitem.html', restaurant_id=restaurant_id)
    return render_template("catalog_create.html")


# "/catalog/<int:catalog_item>/new" - new category item
@app.route("/catalog/<int:catalog_id>/new")
def create_catalog_item(catalog_id):
    return render_template("catalog_item_create.html")


# UPDATE
# "/catalog/<int:catalog_item>/edit" - edit a category
@app.route("/catalog/<int:catalog_id>/edit")
def edit_catalog(catalog_id):
    item = {"name": "My Fav Catalog"}
    return render_template("catalog_edit.html", catalog=item)


# "/catalog/<int:catalog_item>/<int:item_id>/edit" - edit a category
@app.route("/catalog/<int:catalog_id>/<int:item_id>/edit")
def edit_catalog_item(catalog_id, item_id):
    item = {"name": "Skateboard", "description": "Wooden board with roller skate wheels"}
    return render_template("catalog_item_edit.html", catalog_item=item)


# DELETE
# "/catalog/<int:catalog_item>/delete" - delete a category
@app.route("/catalog/<int:catalog_id>/delete")
def delete_catalog(catalog_id):
    item = {"name": "Sports"}
    return render_template("catalog_delete.html", catalog=item)


# "/catalog/<int:catalog_item>/<int:item_id>/delete" - delete a category
@app.route("/catalog/<int:catalog_id>/<int:item_id>/delete")
def delete_catalog_item(catalog_id, item_id):
    item = {"name": "Skateboard", "description": "Wooden board with roller skate wheels"}
    return render_template("catalog_item_delete.html", catalog_item=item)


# LOGIN
# "/catalog/login"
@app.route("/catalog/login")
def login():
    return "login"


# "/catalog/fbconnect"
@app.route("/catalog/fbconnect")
def fb_login():
    return "fbconnect"


# "/catalog/gconnect"
@app.route("/catalog/gconnect")
def g_login():
    return "gconnect"


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

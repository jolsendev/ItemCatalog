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


# READ
# "/" home shows categories and a list of the latest items worked on.
@app.route("/")
@app.route("/catalog")
def show_catalogs():
    catalogs = session.query(Catalog)
    items = {}  # session.query(CatalogItem).filter_by(catalog_id=catalogs.id)
    return render_template("catalog_home.html", catalog_list=catalogs, catalog_items_list=items)


# "/catalog/<int:catalog_item>/items"  show a lost of items for a catagory item
@app.route("/catalog/<int:catalog_id>")
def show_catalog_items(catalog_id):
    catalogs = session.query(Catalog)
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    items = session.query(CatalogItem).filter_by(catalog_id=catalog_id)
    return render_template("catalog_home_items.html", catalog_list=catalogs, catalog=catalog, catalog_items_list=items)


# "/catalog/<int:catalog_id>/<int:item_id>" - shows the description for a single item
@app.route("/catalog/<int:catalog_id>/item/<int:item_id>/description")
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
        new_catalog = Catalog(name=request.form["name"], description=request.form["description"])
        session.add(new_catalog)
        session.commit()
        return redirect(url_for('show_catalog_items', catalog_id=new_catalog.id))
    # if request.method == 'POST':
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
@app.route("/catalog/<int:catalog_id>/new", methods=["GET", "POST"])
def create_catalog_item(catalog_id):
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
            print "My catalog_id = %s" % catalog_item.id
            return redirect(url_for('show_catalog_items', catalog_id=catalog_item.catalog_id))
        except SQLAlchemyError as e:
            print e.message

    return render_template("catalog_item_create.html", catalog=catalog)


# UPDATE
# "/catalog/<int:catalog_item>/edit" - edit a category
@app.route("/catalog/<int:catalog_id>/edit", methods=["GET", "POST"])
def edit_catalog(catalog_id):
    edited_catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    if request.method == 'POST':
        if request.form['name']:
            edited_catalog.name = request.form['name']
        if request.form['description']:
            edited_catalog.description = request.form['description']
        session.add(edited_catalog)
        session.commit()
        return redirect(url_for('show_catalog_items', catalog_id=edited_catalog.id))
    else:
        return render_template("catalog_edit.html", catalog=edited_catalog)


# "/catalog/<int:catalog_item>/<int:item_id>/edit" - edit a category
@app.route("/catalog/<int:catalog_id>/item/<int:item_id>/edit", methods=["POST", "GET"])
def edit_catalog_item(catalog_id, item_id):
    items = session.query(CatalogItem).filter_by(id=item_id)
    item = items.filter_by(catalog_id=catalog_id).one()
    if request.method == "POST":
        if request.form["name"]:
            item.name = request.form["name"]
        if request.form["description"]:
            item.description = request.form["description"]
        session.add(item)
        session.commit()
        return redirect(url_for('show_catalog_items', catalog_id=catalog_id))

    return render_template("catalog_item_edit.html", catalog_id=catalog_id, item=item)


# DELETE
# "/catalog/<int:catalog_item>/delete" - delete a category
@app.route("/catalog/<int:catalog_id>/delete", methods=["GET", "POST"])
def delete_catalog(catalog_id):
    item_to_delete = session.query(Catalog).filter_by(id=catalog_id).one()

    if request.method == "POST":
        no = request.form.get('No', None)
        if no != None:
            return redirect(url_for('show_catalog_items', catalog_id=catalog_id))
        else:
            session.query(Catalog).filter_by(id=catalog_id).delete()
            session.commit()
            session.query(CatalogItem).filter_by(catalog_id=catalog_id).delete()
            return redirect(url_for('show_catalogs'))
    else:
        return render_template("catalog_delete.html", catalog=item_to_delete)


# "/catalog/<int:catalog_item>/<int:item_id>/delete" - delete a category
@app.route("/catalog/<int:catalog_id>/item/<int:item_id>/delete", methods=["GET", "POST"])
def delete_catalog_item(catalog_id, item_id):
    items = session.query(CatalogItem).filter_by(id=item_id)
    item = items.filter_by(catalog_id=catalog_id).one()
    if request.method == "POST":
        no = request.form.get('No', None)
        if no != None:
            return redirect(url_for('show_catalog_items', catalog_id=catalog_id))

        else:
            items.filter_by(catalog_id=catalog_id).delete()
            session.commit()
            return redirect(url_for('show_catalog_items', catalog_id=catalog_id))

    else:
        return render_template("catalog_item_delete.html", item=item, catalog_id=catalog_id)


# LOGIN
# "/catalog/login"
@app.route("/catalog/login")
def login():
    return render_template("login.html")


# "/catalog/fbconnect"
@app.route("/catalog/fbconnect")
def fb_login():
    return "fbconnect"


# "/catalog/gconnect"
@app.route("/catalog/gconnect")
def g_login():
    return "gconnect"

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
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

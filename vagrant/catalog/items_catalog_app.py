from flask import Flask

app = Flask(__name__)


# READ
# "/" home shows categories and a list of the latest items worked on.
@app.route("/")
def show_catalogs():
    return "Show all catalogs and recently modified content"


# "/catalog/<int:catalog_item>/items"  show a lost of items for a catagory item
@app.route("/catalog/<int:catalog_item>")
def show_catalog_items(catalog_item):
    return "Show catalog items %s" % catalog_item


# "/catalog/<int:catalog_id>/<int:item_id>" - shows the description for a single item
@app.route("/catalog/<int:catalog_id>/<int:item_id>/description")
def show_item_description(catalog_id, item_id):
    return "Show catalog description for %s item %s" % (catalog_id, item_id)


# CREATE
# "/catalog/new" - new a category
@app.route("/catalog/new")
def create_catalog():
    return "New catalog"


# "/catalog/<int:catalog_item>/new" - new category item
@app.route("/catalog/<int:catalog_id>/new")
def create_catalog_item(catalog_id):
    return "Create new item for catalog %s" % catalog_id


# UPDATE
# "/catalog/<int:catalog_item>/edit" - edit a category
@app.route("/catalog/<int:catalog_id>/edit")
def edit_catalog(catalog_id):
    return "Edit catalog for %s" % catalog_id


# "/catalog/<int:catalog_item>/<int:item_id>/edit" - edit a category
@app.route("/catalog/<int:catalog_id>/<int:item_id>/edit")
def edit_catalog_item(catalog_id, item_id):
    return "Edit catalog item for catalog %s and item %s" % (catalog_id, item_id)


# DELETE
# "/catalog/<int:catalog_item>/delete" - delete a category
@app.route("/catalog/<int:catalog_id>/delete")
def delete_catalog(catalog_id):
    return "Delete catalog %s" % catalog_id


# "/catalog/<int:catalog_item>/<int:item_id>/delete" - delete a category
@app.route("/catalog/<int:catalog_id>/<int:item_id>/delete")
def delete_catalog_item(catalog_id, item_id):
    return "delete catalog item for catalog %s and item %s" % (catalog_id, item_id)


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

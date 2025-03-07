import json.decoder
import logging
from time import sleep

import requests.exceptions
from flask import Flask, jsonify, request, render_template, url_for
from flask_babel import Babel, _

from config import LOG_LEVEL, API_KEYS, API_PORT
from main import update_products_in_mealie, update_grocy_shoppinglist_from_mealie, compare_product_databases, \
    test_grocy_connection, test_mealie_connection

logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)-8s - %(name)-10s - %(message)s')

app = Flask(__name__)


# Tranlations
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'de']
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'


def get_locale():
    return request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES'])


babel = Babel(app, locale_selector=get_locale)


@app.route('/update-mealie-products', methods=['GET'])
def update_mealie_products():
    if not check_auth(request):
        return response_unauthorized()

    update_products_in_mealie()
    return jsonify({"success": True})


@app.route('/update-grocy-shoppinglist', methods=['GET'])
def update_grocy_shoppinglist():
    if not check_auth(request):
        return response_unauthorized()

    # Call method async
    # thread = threading.Thread(target=update_grocy_shoppinglist_from_mealie)
    # thread.start()

    result = update_grocy_shoppinglist_from_mealie()
    return jsonify({"success": True, "message": _("Mealie shopping list transfered to Grocy"), "result": result})


@app.route('/compare-product-databases', methods=['GET'])
def compare_m2g_databases():
    if not check_auth(request):
        return response_unauthorized()

    result = compare_product_databases()
    return jsonify({"success": True, "message": _("Compare Productdatabases"), "result": result})


@app.route('/health', methods=['GET'])
def health_check():
    grocy_connection = False
    mealie_connection = False

    logging.info(request.headers.get('Accept-Language'))

    retries = 3
    while not grocy_connection and retries > 0:
        # Grocy sometimes fails to respond correctly, so we retry a few times
        try:
            grocy_connection = test_grocy_connection()
            logging.info(f"Grocy connection: {grocy_connection}")
            mealie_connection = test_mealie_connection()
            logging.info(f"Mealie connection: {mealie_connection}")
        except requests.exceptions.ConnectionError or json.JSONDecodeError:
            logging.error(f"Connection Error observed. Retrying {retries} more times.")
            retries -= 1
            sleep(.2)
        except Exception as e:
            logging.error(f"Unknown error: {e}")
            return jsonify({"status": "error", "message": str(e)})

    return jsonify({"status": "alive" if grocy_connection and mealie_connection else "no connection", "grocy_connection": grocy_connection, "mealie_connection": mealie_connection})


@app.route('/')
def index():
    return render_template('index.html', ingress_url_for=ingress_url_for, ingress_username=ingress_username)


def is_ingress():
    return request.headers.get('X-Ingress-Path', None) is not None


def ingress_url_for(url: str):
    ingress_path = request.headers.get('X-Ingress-Path', "")
    return ingress_path + url_for(url)


def ingress_username():
    return request.headers.get('X-Remote-User-Display-Name', None)


def check_auth(request) -> bool:
    return True  # Disable authentication for ingress

    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer ") or len(auth_header.split(" ")) != 2:
        logging.warning("Unauthorized request denied.")
        return False

    token = auth_header.split(" ")[1]
    if token in API_KEYS:
        return True


def response_unauthorized():
    return jsonify({"error": "Unauthorized", "message": _("Not logged in.")}), 403


if __name__ == '__main__':
    # Flask dev only, see wsgi.py for prod
    app.run(debug=False, port=API_PORT)

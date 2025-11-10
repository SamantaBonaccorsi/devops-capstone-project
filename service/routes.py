"""
Account Service

This microservice handles the lifecycle of Accounts
"""
# pylint: disable=unused-import
import json
from flask import jsonify, request, make_response, abort, url_for   # noqa; F401
import logging
from service.models import Account
from service.common import status  # HTTP Status Codes
from . import app  # Import Flask application


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Account REST API Service",
            version="1.0",
            # paths=url_for("list_accounts", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
# CREATE A NEW ACCOUNT
######################################################################
@app.route("/accounts", methods=["POST"])
def create_accounts():
    """
    Creates an Account
    This endpoint will create an Account based the data in the body that is posted
    """
    app.logger.info("Request to create an Account")
    check_content_type("application/json")
    account = Account()
    account.deserialize(request.get_json())
    account.create()
    message = account.serialize()
    # Uncomment once get_accounts has been implemented
    # location_url = url_for("get_accounts", account_id=account.id, _external=True)
    location_url = "/"  # Remove once get_accounts has been implemented
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

######################################################################
# LIST ALL ACCOUNTS
######################################################################

@app.route("/accounts", methods=["GET"])
def list_all_account():
    """
    List all the account
    """
    app.logger.info("Request to list all the Accounts")
    accounts = Account()
    list = accounts.all()
    
    # Converte ogni oggetto in un dizionario
    result = []
    for account in list:
        result.append({
           "id": account.id,
            "name": account.name,
            "email": account.email,
            "address": account.address,
            "phone_number": account.phone_number,
            "date_joined": account.date_joined.isoformat()
        })

    # Restituisce la lista in formato JSON
    return jsonify(result)


######################################################################
# READ AN ACCOUNT
######################################################################

@app.route("/accounts/<int:id>", methods=["GET"])
def read_an_account(id):
    """
    Read an Account
    This endpoint will read an Account based on the path param id
    """
    logging.info(f"VALORE ID ROUTES {id}")
        
    account = Account()
    found = account.find(id)
    
    if (found):
        message = found.serialize()
        return make_response(
        jsonify(message), status.HTTP_200_OK
        )
    else:
        return make_response(
        "Not Found", status.HTTP_404_NOT_FOUND
        )

######################################################################
# UPDATE AN EXISTING ACCOUNT
######################################################################

@app.route("/accounts/<int:id>", methods=["PUT"])
def update_an_account(id):
    """
    Update an Account
    This endpoint will update an Account based on the params id
    """
    app.logger.info("Request to update an Account")
    check_content_type("application/json")
    
    logging.info(f"VALORE ID ROUTES DA AGGIORNARE {id}")
        
    account = Account()
    found = account.find(id)
    
    if (found):
        account.deserialize(request.get_json())
        account.id = id
        account.update()
        message = account.serialize()
        return make_response(
            jsonify(message), status.HTTP_200_OK
        )
    else:
        # l’oggetto con un certo ID non è presente nel database.
        return make_response(
            "Not Found", status.HTTP_404_NOT_FOUND
        )

######################################################################
# DELETE AN ACCOUNT
######################################################################

@app.route("/accounts/<int:id>", methods=["DELETE"])
def delete_an_account(id):
    """
    Read an Account
    This endpoint will read an Account based on the path param id
    """
    logging.info(f"VALORE ID ROUTES DA CANCELLARE {id}")
        
    account = Account()
    found = account.find(id)
    
    if (found):
        found.delete()
        return make_response("", status.HTTP_204_NO_CONTENT
        )
    else:
        return make_response(
            "Not Found", status.HTTP_404_NOT_FOUND
        )


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )

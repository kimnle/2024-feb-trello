from datetime import date

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from init import db
from models.card import Card, card_schema, cards_schema
from controllers.comment_controller import comments_bp
from utils import authorise_as_admin

cards_bp = Blueprint("cards", __name__, url_prefix="/cards")

# /cards - GET - fetch all cards
# /cards/<id> - GET - fetch a single cards
# /cards - POST - create a new card
# /cards/<id> - DELETE - delete a card
# /cards/<id> - PUT, PATCH - edit a card

# /cards - GET - fetch all cards
@cards_bp.route("/")
def get_all_cards():
    # fetch all cards and order them according to date in descending order
    stmt = db.select(Card).order_by(Card.date.desc())
    cards = db.session.scalars(stmt)
    return cards_schema.dump(cards)

# /cards/<id> - GET - fetch a single cards
@cards_bp.route("/<int:card_id>")
def get_one_card(card_id):
    stmt = db.select(Card).filter_by(id=card_id)
    # stmt = db.select(Card).where(Card.id==card_id)
    card = db.session.scalar(stmt)
    if card:
        return card_schema.dump(card)
    else:
        return {"error": f"Card with id {card_id} not found"}, 404

# /cards - POST - create a new card
@cards_bp.route("/", methods=["POST"])
@jwt_required
def create_card():
    # get the data from the body of the request
    body_data = card_schema.load(request.get_json())
    # create a new Card model instance
    card = Card(
        title=body_data.get("title"),
        description=body_data.get("description"),
        date=date.today(),
        status=body_data.get("status"),
        priority=body_data.get("priority"),
        user_id=get_jwt_identity()
    )

    # add and commit to DB
    db.session.add(card)
    db.session.commit()
    # respond
    return card_schema.dump(card)

# /cards/<id> - DELETE - delete a card
@cards_bp.route("/<int:card_id>", methods=["DELETE"])
@jwt_required()
def delete_card(card_id):
    # check whether the user is an admin or not
    is_admin = authorise_as_admin()
    if not is_admin:
        return {"error": "User is not authorised to perform this action"}, 403
    # fetch the card from the database
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    # if card
    if card:
        # delete the card
        db.session.delete(card)
        db.session.commit()
        return {"message": f"Card '{card.title}' deleted successfully"}
    # else
    else:
        # return error
        return {"error": f"Card with id {card_id} not found"}, 404
    
# /cards/<id> - PUT, PATCH - edit a card
@cards_bp.route("<int:card_id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_card(card_id):
    # get the data from the body of the request
    body_data = card_schema.load(request.get_json(), partial=True)
    # get the card from the database
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    # if card
    if card:
        # if the user is the ownder of the card
        if card.user_id == get_jwt_identity():
            return {"error": "You are not the owner of the card"}, 403
        # update the fields as required
        card.title = body_data.get("title") or card.title
        card.description = body_data.get("description") or card.description
        card.status = body_data.get("status") or card.status
        card.priority = body_data.get("priority") or card.priority
        # commit to the DB
        db.session.commit()
        # return a reponse
        return card_schema.dump(card)
    # else
    else:
        # return an error
        return {"error": f"Card with id {card_id} not found"}, 404
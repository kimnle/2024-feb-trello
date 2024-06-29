from init import db, ma
from marshmallow import fields, validates
from marshmallow.validate import Length, And, Regexp, OneOf
from marshmallow.exceptions import ValidationError

VALID_STATUSES = ("To Do", "Ongoing", "Teseting", "Deployed")
VALID_PRIORITIES = ("Low", "Medium", "High", "Urgent")

class Card(db.Model):
    __tablename__ = "cards"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    date = db.Column(db.String) # Created date
    status = db.Column(db.String)
    priority = db.Column(db.String)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    user = db.relationship("User", back_populates="cards")
    comments = db.relationship("Comment", back_populates="card", cascade = "all, delete")

# {
#     id: 1,
#     title: "Card 1",
#     description: "Card 1 desc",
#     date: "..",
#     status: "..",
#     priority: "..",
#     user_id: 1,
#         id: 1,
#         name: "User 1",
#         email: "user1@email.com"
# },
# comments: [
#     {
#         id: 1,
#         message: "Comment 1"
#     }
# ]

class CardSchema(ma.Schema):

    user = fields.Nested("UserSchema", only=["id", "name", "email"])
    comments = fields.List(fields.Nested("CommentSchema", exclude=["card"]))

    title = fields.String(required=True, validate=And(
        Length(min=2, error="Title must be at least 2 characters long"),
        Regexp('^Za-Z0-9 ]+$', error="Title must have alphanumeric characters only")
    ))

    status = fields.String(validate=OneOf(VALID_STATUSES))

    priority = fields.String(validate=OneOf(VALID_PRIORITIES, error="Invalid Priority"))

    # we have one more requirement - only one card can have a status of Ongoing at a time
    @ validates("status")
    def validate_status(self, value):
        # if trying to set the value of status as "Ongoing"
        if value == VALID_STATUSES[1]:
        # check whether an existing Ongoing card exists or not
        stmt = db.select(db.func.count()).select_from(Card).filter_by(status=VALID_STATUSES[1])
        count = db.session.scalar(stmt)
        # if it exists
        if count > 0:
        # throw error
        raise ValidationError("You already have an ongoing card")

    class Meta:
        fields = ("id", "title", "description", "date", "status", "priority", "user", "comments")
        ordered = True

card_schema = CardSchema()
cards_schema = CardSchema(many=True)
from init import db, ma
from marshmallow import fields

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

    class Meta:
        fields = ("id", "title", "description", "date", "status", "priority", "user", "comments")
        ordered = True

card_schema = CardSchema()
cards_schema = CardSchema(many=True)
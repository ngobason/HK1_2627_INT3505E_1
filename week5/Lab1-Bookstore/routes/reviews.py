from flask import Blueprint, jsonify
from models import Book, Review, User, db
from routes.common import get_or_404, payload_for, save_changes

bp = Blueprint("reviews", __name__)


@bp.get("/reviews")
def list_reviews():
    items = db.session.execute(db.select(Review).order_by(Review.id)).scalars().all()
    return jsonify([item.to_dict() for item in items])


@bp.get("/reviews/<int:review_id>")
def detail_review(review_id):
    return jsonify(get_or_404(Review, review_id).to_dict())


@bp.post("/reviews")
def create_review():
    data = payload_for("review")
    get_or_404(Book, data["book_id"])
    get_or_404(User, data["user_id"])
    item = Review(
        rating=data["rating"],
        comment=data.get("comment"),
        book_id=data["book_id"],
        user_id=data["user_id"],
    )
    db.session.add(item)
    save_changes()
    return jsonify(item.to_dict()), 201, {"Location": f"/api/v1/reviews/{item.id}"}


@bp.patch("/reviews/<int:review_id>")
def update_review(review_id):
    item = get_or_404(Review, review_id)
    data = payload_for("review", partial=True)
    if "book_id" in data:
        get_or_404(Book, data["book_id"])
    if "user_id" in data:
        get_or_404(User, data["user_id"])

    for field in ("rating", "comment", "book_id", "user_id"):
        if field in data:
            setattr(item, field, data[field])
    save_changes()
    return jsonify(item.to_dict())


@bp.delete("/reviews/<int:review_id>")
def delete_review(review_id):
    item = get_or_404(Review, review_id)
    db.session.delete(item)
    save_changes()
    return "", 204

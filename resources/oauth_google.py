from __future__ import annotations

from flask import Blueprint, current_app, jsonify, redirect, url_for

from ..extensions import db, oauth
from ..models import User

bp = Blueprint("oauth_google", __name__)


@bp.get("/api/auth/google/login")
def google_login():
    if oauth is None or not hasattr(oauth, "google"):
        return jsonify({"message": "OAuth not configured"}), 501

    redirect_uri = url_for("oauth_google.google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@bp.get("/api/auth/google/callback")
def google_callback():
    if oauth is None or not hasattr(oauth, "google"):
        return jsonify({"message": "OAuth not configured"}), 501

    oauth.google.authorize_access_token()
    userinfo = oauth.google.userinfo()  # type: ignore[attr-defined]
    data = userinfo if isinstance(userinfo, dict) else getattr(userinfo, "json", lambda: {})()

    sub = data.get("sub")
    email = data.get("email")
    name = data.get("name")
    picture = data.get("picture")

    if not sub or not email:
        return jsonify({"message": "Google login failed"}), 400

    user = User.query.filter((User.provider == "google") & (User.provider_sub == sub)).first()
    if user is None:
        user = User.query.filter(User.email == email).first()
        if user is None:
            user = User(email=email)
            user.set_unusable_password()
            db.session.add(user)

        user.provider = "google"
        user.provider_sub = sub
        if name and not user.name:
            user.name = name
        if picture:
            user.avatar_url = picture
        db.session.commit()

    access = user.create_token()
    frontend_redirect = current_app.config.get(
        "FRONTEND_OAUTH_REDIRECT", "http://localhost:8080/login/oauth"
    )
    return redirect(f"{frontend_redirect}?access_token={access}")

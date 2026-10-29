# app/__init__.py
import logging
import os
from flask import Flask, render_template
from app.config import config
from app.extensions import csrf, db, migrate


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    config_class = config.get(config_name, config["default"])
    if callable(config_class):
        app.config.from_object(config_class())
    else:
        app.config.from_object(config_class)

    # Standard Twelve-Factor logging to stdout
    logging.basicConfig(
        level=logging.INFO if not app.debug else logging.DEBUG,
        format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    )

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Register routes blueprint
    from app.routes import bp as main_bp

    app.register_blueprint(main_bp)

    # Custom HTTP error handlers
    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(f"Internal Server Error: {error}")
        return render_template("errors/500.html"), 500

    return app

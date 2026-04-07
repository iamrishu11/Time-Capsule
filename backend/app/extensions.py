"""
Flask extensions initialization.

Extensions are initialized here without an app instance,
then bound to the app in the application factory.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail

# Database ORM
db = SQLAlchemy()

# Database migrations
migrate = Migrate()

# Email
mail = Mail()

import os


class Config:
    """Application configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # Database — SQLite for development, easily swappable to PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///pos.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Low-stock threshold
    LOW_STOCK_THRESHOLD = 10

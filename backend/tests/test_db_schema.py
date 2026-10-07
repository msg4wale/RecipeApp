from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

from app.models import (
    Base,
    AdminDecision,
    ChefVerification,
    Comment,
    EmailVerificationToken,
    Follow,
    Like,
    Recipe,
    RecipeIngredient,
    RecipeMedia,
    RecipeStep,
    User,
    UserSession,
)


def test_expected_tables_exist() -> None:
    table_names = set(Base.metadata.tables)

    for name in {
        "users",
        "auth_sessions",
        "email_verification_tokens",
        "chef_verifications",
        "admin_decisions",
        "recipes",
        "recipe_ingredients",
        "recipe_steps",
        "recipe_media",
        "likes",
        "comments",
        "follows",
    }:
        assert name in table_names


def test_core_user_and_recipe_columns_exist() -> None:
    user_columns = set(User.__table__.columns.keys())
    recipe_columns = set(Recipe.__table__.columns.keys())

    assert {"id", "email", "display_name", "password_hash", "role", "chef_status", "created_at"}.issubset(user_columns)
    assert {"id", "user_id", "token_hash", "expires_at", "revoked_at", "created_at"}.issubset(
        set(UserSession.__table__.columns.keys())
    )
    assert {"email_verified"}.issubset(set(User.__table__.columns.keys()))
    assert {"id", "user_id", "token_hash", "expires_at", "consumed_at"}.issubset(
        set(EmailVerificationToken.__table__.columns.keys())
    )
    assert {"certificate_ref", "status", "reviewed_by_user_id", "reviewed_at", "rationale"}.issubset(
        set(ChefVerification.__table__.columns.keys())
    )
    assert {
        "id",
        "subject_type",
        "subject_id",
        "actor_user_id",
        "outcome",
        "rationale",
        "created_at",
    }.issubset(set(AdminDecision.__table__.columns.keys()))
    assert {"id", "chef_id", "title", "state", "like_count", "comment_count", "published_at"}.issubset(recipe_columns)

    assert Comment.__table__.columns["recipe_id"].nullable is False
    assert Like.__table__.columns["recipe_id"].nullable is False
    assert Follow.__table__.columns["chef_user_id"].nullable is False


def test_admin_decision_migration_is_single_head_after_chef_review_rationale() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    config = Config(str(backend_dir / "alembic.ini"))
    config.set_main_option("script_location", str(backend_dir / "migrations"))
    scripts = ScriptDirectory.from_config(config)

    assert scripts.get_heads() == ["20261004_add_admin_decisions"]
    admin_decisions = scripts.get_revision("20261004_add_admin_decisions")
    assert admin_decisions is not None
    assert admin_decisions.down_revision == "20260930_chef_review_rationale"

"""initial_schema

Revision ID: f153d9d95cd0
Revises: 
Create Date: 2026-03-10 14:27:46.054713

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f153d9d95cd0'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial schema tables."""
    op.create_table(
        "cards",
        sa.Column("id",          sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("wiki_id",     sa.String(50),  unique=True, nullable=True),
        sa.Column("name",        sa.String(255), nullable=False),
        sa.Column("title",       sa.String(255), nullable=True),
        sa.Column("full_name",   sa.String(512), nullable=True),
        sa.Column("rarity",      sa.String(10),  nullable=True),
        sa.Column("type",        sa.String(10),  nullable=True),
        sa.Column("cost",        sa.Integer,     nullable=True),
        sa.Column("hp_max",      sa.Integer,     nullable=True),
        sa.Column("atk_max",     sa.Integer,     nullable=True),
        sa.Column("def_max",     sa.Integer,     nullable=True),
        sa.Column("hp_eza",      sa.Integer,     nullable=True),
        sa.Column("atk_eza",     sa.Integer,     nullable=True),
        sa.Column("def_eza",     sa.Integer,     nullable=True),
        sa.Column("leader_skill",            sa.Text, nullable=True),
        sa.Column("super_attack",            sa.Text, nullable=True),
        sa.Column("ultra_super_attack",      sa.Text, nullable=True),
        sa.Column("passive_skill",           sa.Text, nullable=True),
        sa.Column("active_skill",            sa.Text, nullable=True),
        sa.Column("active_skill_condition",  sa.Text, nullable=True),
        sa.Column("eza_leader_skill",        sa.Text, nullable=True),
        sa.Column("eza_passive_skill",       sa.Text, nullable=True),
        sa.Column("eza_super_attack",        sa.Text, nullable=True),
        sa.Column("categories",              sa.Text, nullable=True),
        sa.Column("link_skills",             sa.Text, nullable=True),
        sa.Column("awakening_medals",        sa.Text, nullable=True),
        sa.Column("is_transformable",        sa.Boolean, default=False),
        sa.Column("transforms_to_id",        sa.Integer, nullable=True),
        sa.Column("transformation_conditions", sa.Text, nullable=True),
        sa.Column("is_eza",         sa.Boolean, default=False),
        sa.Column("is_lr",          sa.Boolean, default=False),
        sa.Column("is_dokkan_fest", sa.Boolean, default=False),
        sa.Column("image_url",      sa.String(512), nullable=True),
        sa.Column("thumb_url",      sa.String(512), nullable=True),
        sa.Column("wiki_url",       sa.String(512), nullable=True),
        sa.Column("jp_release_date",  sa.String(20), nullable=True),
        sa.Column("glb_release_date", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_cards_name",    "cards", ["name"])
    op.create_index("ix_cards_wiki_id", "cards", ["wiki_id"], unique=True)

    op.create_table(
        "events",
        sa.Column("id",           sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name",         sa.String(255), nullable=False),
        sa.Column("description",  sa.Text,        nullable=True),
        sa.Column("event_type",   sa.String(50),  nullable=True),
        sa.Column("difficulty",   sa.String(50),  nullable=True),
        sa.Column("start_date",   sa.DateTime,    nullable=True),
        sa.Column("end_date",     sa.DateTime,    nullable=True),
        sa.Column("stages",       sa.Integer,     nullable=True),
        sa.Column("stamina_cost", sa.Integer,     nullable=True),
        sa.Column("rewards",      sa.Text,        nullable=True),
        sa.Column("wiki_url",     sa.String(512), nullable=True),
        sa.Column("image_url",    sa.String(512), nullable=True),
        sa.Column("created_at",   sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at",   sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "banners",
        sa.Column("id",            sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name",          sa.String(255), nullable=False),
        sa.Column("description",   sa.Text,        nullable=True),
        sa.Column("banner_type",   sa.String(50),  nullable=True),
        sa.Column("start_date",    sa.DateTime,    nullable=True),
        sa.Column("end_date",      sa.DateTime,    nullable=True),
        sa.Column("featured_cards", sa.Text,       nullable=True),
        sa.Column("summon_rates",  sa.Text,        nullable=True),
        sa.Column("wiki_url",      sa.String(512), nullable=True),
        sa.Column("image_url",     sa.String(512), nullable=True),
        sa.Column("created_at",    sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at",    sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "items",
        sa.Column("id",           sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name",         sa.String(255), nullable=False),
        sa.Column("description",  sa.Text,        nullable=True),
        sa.Column("item_type",    sa.String(50),  nullable=True),
        sa.Column("effect",       sa.Text,        nullable=True),
        sa.Column("rarity",       sa.String(20),  nullable=True),
        sa.Column("how_to_obtain", sa.Text,       nullable=True),
        sa.Column("image_url",    sa.String(512), nullable=True),
        sa.Column("created_at",   sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at",   sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table("items")
    op.drop_table("banners")
    op.drop_table("events")
    op.drop_index("ix_cards_wiki_id", "cards")
    op.drop_index("ix_cards_name",    "cards")
    op.drop_table("cards")

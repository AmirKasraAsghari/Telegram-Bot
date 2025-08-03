"""create pair_sentiment table"""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pair_sentiment",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("pair", sa.String, nullable=False),
        sa.Column("ts", sa.DateTime, nullable=False),
        sa.Column("score", sa.Float, nullable=False),
        sa.Column("summary", sa.String(length=120), nullable=False),
    )
    op.create_index("ix_pair_sentiment_pair", "pair_sentiment", ["pair"])
    op.create_index("ix_pair_sentiment_ts", "pair_sentiment", ["ts"])


def downgrade() -> None:
    op.drop_table("pair_sentiment")

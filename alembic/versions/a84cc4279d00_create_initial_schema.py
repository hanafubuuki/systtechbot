"""create_initial_schema

Revision ID: a84cc4279d00
Revises:
Create Date: 2025-10-16 17:55:16.798076

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a84cc4279d00"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema: Create users, chats, and messages tables."""
    # Create users table
    op.execute("""
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            telegram_user_id BIGINT NOT NULL UNIQUE,
            first_name VARCHAR(255),
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            deleted_at TIMESTAMP
        )
    """)

    # Create chats table
    op.execute("""
        CREATE TABLE chats (
            id SERIAL PRIMARY KEY,
            telegram_chat_id BIGINT NOT NULL UNIQUE,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            deleted_at TIMESTAMP
        )
    """)

    # Create messages table
    op.execute("""
        CREATE TABLE messages (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            chat_id INTEGER NOT NULL REFERENCES chats(id),
            role VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            length INTEGER NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            deleted_at TIMESTAMP
        )
    """)

    # Create index for efficient message retrieval
    op.execute("""
        CREATE INDEX idx_messages_user_chat
        ON messages(user_id, chat_id, deleted_at, created_at)
    """)


def downgrade() -> None:
    """Downgrade schema: Drop all tables."""
    op.execute("DROP TABLE IF EXISTS messages CASCADE")
    op.execute("DROP TABLE IF EXISTS chats CASCADE")
    op.execute("DROP TABLE IF EXISTS users CASCADE")

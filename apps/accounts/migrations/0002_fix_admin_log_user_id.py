"""
Fix type mismatch on legacy RDS databases.

V1 schema had accounts_users with UUID primary key, causing django_admin_log.user_id
to be stored as UUID. V2 uses accounts_user with BigAutoField (bigint) primary key.

Only runs on PostgreSQL — SQLite (tests) is skipped automatically.
"""

from django.db import migrations


def fix_admin_log_user_id(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    with schema_editor.connection.cursor() as cursor:
        # Check current type of django_admin_log.user_id
        cursor.execute(
            """
            SELECT data_type
            FROM information_schema.columns
            WHERE table_name = 'django_admin_log'
              AND column_name = 'user_id'
            """
        )
        row = cursor.fetchone()
        if not row or row[0] != "uuid":
            return  # Nothing to fix

        # Drop all FK constraints on user_id
        cursor.execute(
            """
            SELECT tc.constraint_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
            WHERE tc.table_name = 'django_admin_log'
              AND tc.constraint_type = 'FOREIGN KEY'
              AND kcu.column_name = 'user_id'
            """
        )
        constraints = [r[0] for r in cursor.fetchall()]
        for constraint in constraints:
            cursor.execute(
                f"ALTER TABLE django_admin_log DROP CONSTRAINT IF EXISTS {constraint}"
            )

        # Truncate (UUID values cannot be directly cast to bigint)
        cursor.execute("TRUNCATE django_admin_log")

        # Change column type to bigint
        cursor.execute(
            "ALTER TABLE django_admin_log ALTER COLUMN user_id TYPE bigint USING 0"
        )

        # Re-add FK to new accounts_user table
        cursor.execute(
            """
            ALTER TABLE django_admin_log
                ADD CONSTRAINT django_admin_log_user_id_v2_fk
                FOREIGN KEY (user_id)
                REFERENCES accounts_user(id)
                DEFERRABLE INITIALLY DEFERRED
            """
        )


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            fix_admin_log_user_id,
            reverse_code=migrations.RunPython.noop,
        ),
    ]

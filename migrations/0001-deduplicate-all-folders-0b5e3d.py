#    Copyright 2025 Genesis Corporation.
#
#    All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from restalchemy.storage.sql import migrations


class MigrationStep(migrations.AbstarctMigrationStep):

    def __init__(self):
        self._depends = ["0000-init-folders-and-items-f72eb7.py"]

    @property
    def migration_id(self):
        return "0b5e3d4c-9c9a-4b6b-9f4e-f7f6d6a3fd8d"

    @property
    def is_manual(self):
        return False

    def upgrade(self, session):
        expressions = [
            """
            WITH ranked AS (
                SELECT
                    uuid,
                    user_id,
                    created_at,
                    ROW_NUMBER() OVER (
                        PARTITION BY user_id
                        ORDER BY created_at ASC, uuid ASC
                    ) AS rn
                FROM folders
                WHERE system_type = 'all'
            ),
            keep AS (
                SELECT user_id, uuid AS keep_uuid
                FROM ranked
                WHERE rn = 1
            ),
            dups AS (
                SELECT uuid AS dup_uuid, user_id
                FROM ranked
                WHERE rn > 1
            )
            DELETE FROM folder_items AS fi
            USING dups
            JOIN keep ON keep.user_id = dups.user_id
            WHERE fi.folder = dups.dup_uuid
                AND EXISTS (
                    SELECT 1
                    FROM folder_items AS fi_keep
                    WHERE fi_keep.folder = keep.keep_uuid
                        AND fi_keep.chat_id = fi.chat_id
                );
            """,
            """
            WITH ranked AS (
                SELECT
                    uuid,
                    user_id,
                    created_at,
                    ROW_NUMBER() OVER (
                        PARTITION BY user_id
                        ORDER BY created_at ASC, uuid ASC
                    ) AS rn
                FROM folders
                WHERE system_type = 'all'
            ),
            keep AS (
                SELECT user_id, uuid AS keep_uuid
                FROM ranked
                WHERE rn = 1
            ),
            dups AS (
                SELECT uuid AS dup_uuid, user_id
                FROM ranked
                WHERE rn > 1
            )
            UPDATE folder_items AS fi
            SET folder = keep.keep_uuid
            FROM dups
            JOIN keep ON keep.user_id = dups.user_id
            WHERE fi.folder = dups.dup_uuid;
            """,
            """
            WITH ranked AS (
                SELECT
                    uuid,
                    user_id,
                    created_at,
                    ROW_NUMBER() OVER (
                        PARTITION BY user_id
                        ORDER BY created_at ASC, uuid ASC
                    ) AS rn
                FROM folders
                WHERE system_type = 'all'
            )
            DELETE FROM folders
            WHERE uuid IN (SELECT uuid FROM ranked WHERE rn > 1);
            """,
            """
            CREATE UNIQUE INDEX IF NOT EXISTS "folders_one_all_per_user_idx"
                ON "folders" ("user_id")
                WHERE (system_type = 'all');
            """,
        ]

        for expression in expressions:
            session.execute(expression)

    def downgrade(self, session):
        expressions = [
            'DROP INDEX IF EXISTS "folders_one_all_per_user_idx";',
        ]

        for expression in expressions:
            session.execute(expression)


migration_step = MigrationStep()

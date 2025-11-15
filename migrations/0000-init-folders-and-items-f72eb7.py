#    Copyright 2016 Eugene Frolov <eugene@frolov.net.ru>
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
        self._depends = []

    @property
    def migration_id(self):
        return "f72eb746-75cc-4a75-87c1-143091726f78"

    @property
    def is_manual(self):
        return False

    def upgrade(self, session):
        expressions = [
            """
            CREATE TABLE IF NOT EXISTS "folders" (
                "uuid" UUID PRIMARY KEY,
                "title" VARCHAR(64) NOT NULL,
                "user_id" INTEGER NOT NULL,
                "background_color_value" BIGINT NULL,
                "unread_messages" JSONB[] NOT NULL,
                "system_type" VARCHAR(16) NULL
                    CHECK (system_type IN ('all', 'created')),
                "created_at" TIMESTAMP(6) NOT NULL DEFAULT NOW(),
                "updated_at" TIMESTAMP(6) NOT NULL DEFAULT NOW()
            );
            """,
            """
            CREATE INDEX "folders_title_idx" ON "folders" ("title");
            """,
            """
            CREATE TABLE IF NOT EXISTS "folder_items" (
                "uuid" UUID PRIMARY KEY,
                "folder" UUID NOT NULL,
                "user_id" INTEGER NOT NULL,
                "chat_id" INTEGER NOT NULL,
                "order_index" INTEGER NULL,
                "pinned_at" TIMESTAMP(6) NULL,
                "created_at" TIMESTAMP(6) NOT NULL DEFAULT NOW(),
                "updated_at" TIMESTAMP(6) NOT NULL DEFAULT NOW(),
                CONSTRAINT "folder_items_folder_uuid_fkey"
                    FOREIGN KEY ("folder") REFERENCES "folders" ("uuid")
                    ON DELETE CASCADE
            );
            """,
            """
            CREATE INDEX "folder_items_folder_idx"
                ON "folder_items" ("folder");
            """,
            """
            CREATE UNIQUE INDEX "chat_id_folder_idx"
                ON "folder_items" ("chat_id", "folder");
            """,
        ]

        for expression in expressions:
            session.execute(expression)

    def downgrade(self, session):
        tables = ["folder_items", "folders"]

        for table in tables:
            self._delete_table_if_exists(session, table)


migration_step = MigrationStep()

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

import datetime

from restalchemy.api import actions as ra_actions
from restalchemy.api import controllers as ra_controllers
from restalchemy.api import resources as ra_resources
from restalchemy.common import exceptions as ra_exc
from restalchemy.dm import filters as dm_filters

from workspace.user_api.api import versions
from workspace.user_api.dm import models


class ApiEndpointController(ra_controllers.RoutesListController):
    """Controller for /v1/ endpoint"""

    __TARGET_PATH__ = f"/{versions.API_VERSION_1_0}/"


class UserScopedMixin:

    def _get_user_id(self):
        ctx = self.get_context()
        user_id = getattr(ctx, "user_id", None) if ctx is not None else None
        if user_id is None:
            raise ra_exc.ValidationErrorException()
        return user_id


class FolderController(
    UserScopedMixin, ra_controllers.BaseResourceControllerPaginated
):
    __resource__ = ra_resources.ResourceByRAModel(
        model_class=models.Folder,
        hidden_fields=["user_id"],
        convert_underscore=False,
    )

    def create(self, **kwargs):
        user_id = self._get_user_id()
        kwargs["user_id"] = user_id
        return super().create(**kwargs)

    def get(self, uuid):
        user_id = self._get_user_id()
        return self.model.objects.get_one(
            filters={
                "uuid": dm_filters.EQ(uuid),
                "user_id": dm_filters.EQ(user_id),
            },
        )

    def filter(self, filters, **kwargs):
        user_id = self._get_user_id()
        filters = (filters or {}).copy()
        filters["user_id"] = dm_filters.EQ(user_id)
        return super().filter(filters=filters, **kwargs)

    def delete(self, uuid):
        dm = self.get(uuid=uuid)
        dm.delete()

    def update(self, uuid, **kwargs):
        dm = self.get(uuid=uuid)
        dm.update_dm(values=kwargs)
        dm.update()
        return dm


class FolderItemController(
    UserScopedMixin,
    ra_controllers.BaseNestedResourceControllerPaginated,
):
    __resource__ = ra_resources.ResourceByModelWithCustomProps(
        model_class=models.FolderItem,
        hidden_fields=["folder", "user_id"],
        convert_underscore=False,
    )
    __pr_name__ = "folder"

    def create(self, parent_resource, **kwargs):
        user_id = self._get_user_id()
        kwargs["user_id"] = user_id
        return super().create(parent_resource=parent_resource, **kwargs)

    def get(self, parent_resource, uuid):
        user_id = self._get_user_id()
        return self.model.objects.get_one(
            filters={
                self.__pr_name__: dm_filters.EQ(parent_resource),
                "uuid": dm_filters.EQ(uuid),
                "user_id": dm_filters.EQ(user_id),
            },
        )

    def filter(self, parent_resource, filters, **kwargs):
        user_id = self._get_user_id()
        filters = (filters or {}).copy()
        filters["user_id"] = dm_filters.EQ(user_id)
        return super().filter(
            parent_resource=parent_resource,
            filters=filters,
            **kwargs,
        )

    def delete(self, parent_resource, uuid):
        dm = self.get(parent_resource=parent_resource, uuid=uuid)
        dm.delete()

    def update(self, parent_resource, uuid, **kwargs):
        dm = self.get(parent_resource=parent_resource, uuid=uuid)
        dm.update_dm(values=kwargs)
        dm.update()
        return dm

    @ra_actions.post
    def pin(self, resource, *args, **kwargs):
        resource.pinned_at = datetime.datetime.now(datetime.timezone.utc)
        resource.save()
        return resource

    @ra_actions.post
    def unpin(self, resource, *args, **kwargs):
        resource.pinned_at = None
        resource.save()
        return resource


class FolderItemsController(
    UserScopedMixin,
    ra_controllers.BaseResourceControllerPaginated,
):
    __resource__ = ra_resources.ResourceByModelWithCustomProps(
        model_class=models.FolderItemRAFix,
        hidden_fields=["folder", "user_id"],
        convert_underscore=False,
    )

    def filter(self, filters, **kwargs):
        user_id = self._get_user_id()
        filters = (filters or {}).copy()
        filters["user_id"] = dm_filters.EQ(user_id)
        return super().filter(filters=filters, **kwargs)

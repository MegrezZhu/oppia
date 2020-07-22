# coding: utf-8
#
# Copyright 2014 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Models relating to configuration properties and platform parameters."""

from __future__ import absolute_import  # pylint: disable=import-only-modules
from __future__ import unicode_literals  # pylint: disable=import-only-modules

import core.storage.base_model.gae_models as base_models

from google.appengine.ext import ndb


class ConfigPropertySnapshotMetadataModel(
        base_models.BaseSnapshotMetadataModel):
    """Storage model for the metadata for a config property snapshot."""

    pass


class ConfigPropertySnapshotContentModel(base_models.BaseSnapshotContentModel):
    """Storage model for the content for a config property snapshot."""

    pass


class ConfigPropertyModel(base_models.VersionedModel):
    """A class that represents a named configuration property.

    The id is the name of the property.
    """

    SNAPSHOT_METADATA_CLASS = ConfigPropertySnapshotMetadataModel
    SNAPSHOT_CONTENT_CLASS = ConfigPropertySnapshotContentModel

    # The property value.
    value = ndb.JsonProperty(indexed=False)

    @staticmethod
    def get_deletion_policy():
        """ConfigPropertyModel is not related to users."""
        return base_models.DELETION_POLICY.NOT_APPLICABLE

    @staticmethod
    def get_export_policy():
        """Model does not contain user data."""
        return base_models.EXPORT_POLICY.NOT_APPLICABLE

    def commit(self, committer_id, commit_cmds):
        super(ConfigPropertyModel, self).commit(committer_id, '', commit_cmds)


class PlatformParameterSnapshotMetadataModel(
        base_models.BaseSnapshotMetadataModel):
    """Storage model for the metadata for a platform parameter snapshot."""

    pass


class PlatformParameterSnapshotContentModel(
        base_models.BaseSnapshotContentModel):
    """Storage model for the content for a platform parameter snapshot."""

    pass


class PlatformParameterModel(base_models.VersionedModel):
    """A class that represents a named dynamic platform parameter.
    This model only stores fields that can be updated in run time.

    The id is the name of the parameter.
    """

    SNAPSHOT_METADATA_CLASS = PlatformParameterSnapshotMetadataModel
    SNAPSHOT_CONTENT_CLASS = PlatformParameterSnapshotContentModel

    rules = ndb.JsonProperty(repeated=True)
    rule_schema_version = ndb.IntegerProperty(required=True, indexed=True)

    @staticmethod
    def get_deletion_policy():
        """PlatformParameterModel is not related to users."""
        return base_models.DELETION_POLICY.NOT_APPLICABLE

    @staticmethod
    def get_export_policy():
        """Model does not contain user data."""
        return base_models.EXPORT_POLICY.NOT_APPLICABLE

    @classmethod
    def create(cls, param_name, rule_dicts, rule_schema_version):
        """Creates a PlatformParameterModel instance.

        Args:
            param_name: str. The name of the parameter, which is immutable.
            rule_dicts: list(dict). List of dict representation of
                PlatformParameterRule objects, which have the following
                structure:
                    - value_when_matched: *. The result of the rule when it's
                        matched.
                    - filters: list(dict). List of dict representation of
                        PlatformParameterFilter objects, having the following
                        structure:
                            - type: str. The type of the filter.
                            - value: *. The value of the filter to match
                                against.

        Returns:
            PlatformParameterModel. The created PlatformParameterModel
            instance.
        """
        return cls(
            id=param_name,
            rules=rule_dicts,
            rule_schema_version=rule_schema_version)

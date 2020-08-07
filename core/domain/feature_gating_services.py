# coding: utf-8
#
# Copyright 2020 The Oppia Authors. All Rights Reserved.
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

"""The service for gating features.

This service provides two interfaces to access the feature flag values for
clients and servers respectively.

For clients, please use 'evaluate_all_feature_flag_value_for_client' from
request handlers with client context.

For servers, please directly call 'evaluate_feature_flag_value_for_server' with
the name of the feature.

For more details of the usage of these two method, please refer their docstrings
in this file.
"""

from __future__ import absolute_import  # pylint: disable=import-only-modules
from __future__ import unicode_literals  # pylint: disable=import-only-modules

from constants import constants
from core import platform_feature_list
from core.domain import platform_parameter_domain as param_domain
from core.domain import platform_parameter_registry as registry


ALL_FEATURES_LIST = (
    platform_feature_list.DEV_FEATURES_LIST +
    platform_feature_list.TEST_FEATURES_LIST +
    platform_feature_list.PROD_FEATURES_LIST
)

ALL_FEATURES_NAMES_SET = set(ALL_FEATURES_LIST)


def create_evaluation_context_for_client(client_context_dict):
    """Returns context instance for evaluation, using the information
    provided by clients.

    Args:
        client_context_dict: dict. The client side context.

    Returns:
        EvaluationContext. The context for evaluation.
    """
    return param_domain.EvaluationContext.from_dict(
        client_context_dict,
        {
            'server_mode': _get_server_mode()
        }
    )


def get_all_feature_flag_dicts():
    """Returns dict representations of all feature flags.

    Returns:
        dict. The keys are the feature names and the values are the dict
        mappings of all fields of the feature flags.
    """
    return [
        registry.Registry.get_platform_parameter(name).to_dict()
        for name in ALL_FEATURES_LIST
    ]


def evaluate_all_feature_flag_value_for_client(context):
    """Evaluates and returns the values for all feature flags.

    Args:
        context: EvaluationContext. The context used for evaluation.

    Returns:
        dict. The keys are the feature names and the values are boolean
        results of corresponding flags.
    """
    return _evaluate_feature_flag_values_for_context(
        ALL_FEATURES_LIST, context)


def evaluate_feature_flag_value_for_server(feature_name):
    """Evaluates and returns the values of the feature flag, using context
    from the server only.

    Args:
        feature_name: str. The name of the feature flag that needs to
            be evaluated.

    Returns:
        bool. The value of the feature flag, True if it's enabled.
    """
    context = _create_evaluation_context_for_server()
    values_dict = _evaluate_feature_flag_values_for_context(
        [feature_name], context)
    return values_dict[feature_name]


def update_feature_flag_rules(
        feature_name, committer_id, commit_message, new_rule_dicts):
    """Updates the feature flag's rules.

    Args:
        feature_name: str. The name of the feature to update.
        committer_id: str. ID of the committer.
        commit_message: str. The commit message.
        new_rule_dicts: list(dist). A list of dict mappings of all fields
            of PlatformParameterRule object.
    """
    if feature_name not in ALL_FEATURES_NAMES_SET:
        raise Exception('Feature flag not exist: %s.' % feature_name)

    registry.Registry.update_platform_parameter(
        feature_name, committer_id, commit_message, new_rule_dicts)


# TODO(MegrezZhu): Currently Oppia runs in either of the two modes:
# dev or prod. There should be another mode 'test' added for QA testing,
# once it is added, this function needs to be updated to take that into
# consideration.
def _get_server_mode():
    """Returns the running mode of Oppia.

    Returns:
        str. The server mode of Oppia, 'dev' if Oppia is running in development
        mode, 'prod' if in production mode.
    """
    if constants.DEV_MODE:
        return param_domain.SERVER_MODES.dev
    else:
        return param_domain.SERVER_MODES.prod


def _create_evaluation_context_for_server():
    """Returns evaluation context with information of the server.

    Returns:
        EvaluationContext. The context for evaluation.
    """
    return param_domain.EvaluationContext.from_dict(
        {
            'client_type': None,
            'browser_type': None,
            'app_version': None,
            'user_locale': None,
        },
        {
            'server_mode': _get_server_mode()
        }
    )


def _evaluate_feature_flag_values_for_context(feature_names, context):
    """Evaluates and returns the values for specified feature flags.

    Args:
        feature_names: list(str). The names of feature flags that need to
            be evaluated.
        context: EvaluationContext. The context used for evaluation.

    Returns:
        dict. The keys are the feature names and the values are boolean
        results of corresponding flags.
    """
    unknown_feature_names = []
    for feature_name in feature_names:
        if feature_name not in ALL_FEATURES_NAMES_SET:
            unknown_feature_names.append(feature_name)
    if len(unknown_feature_names) > 0:
        raise Exception(
            'Unknown feature flag(s): %s.' % unknown_feature_names)

    result_dict = {}
    for feature_name in feature_names:
        flag_domain = registry.Registry.get_platform_parameter(
            feature_name)
        result_dict[feature_name] = flag_domain.evaluate(context)
    return result_dict

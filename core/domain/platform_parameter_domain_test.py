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

"""Tests for the domain objects relating to platform parameters."""

from __future__ import absolute_import  # pylint: disable=import-only-modules
from __future__ import unicode_literals  # pylint: disable=import-only-modules

from core.domain import platform_parameter_domain as parameter_domain
from core.platform import models
from core.tests import test_utils
import feconf
import utils


(config_models,) = models.Registry.import_models(
    [models.NAMES.config])
memcache_services = models.Registry.import_memcache_services()


class PlatformParameterChangeTests(test_utils.GenericTestBase):
    """Test for the PlatformParameterChange class."""

    CMD_EDIT_RULES = parameter_domain.PlatformParameterChange.CMD_EDIT_RULES

    def test_param_change_object_with_missing_cmd_raises_exception(self):
        with self.assertRaisesRegexp(
            utils.ValidationError, 'Missing cmd key in change dict'):
            parameter_domain.PlatformParameterChange({'invalid': 'data'})

    def test_param_change_object_with_invalid_cmd_raises_exception(self):
        with self.assertRaisesRegexp(
            utils.ValidationError, 'Command invalid is not allowed'):
            parameter_domain.PlatformParameterChange({'cmd': 'invalid'})

    def test_param_change_object_missing_attribute_in_cmd_raises_exception(
            self):
        with self.assertRaisesRegexp(
            utils.ValidationError,
            'The following required attributes are missing: new_rules'):
            parameter_domain.PlatformParameterChange({
                'cmd': self.CMD_EDIT_RULES
            })

    def test_param_change_object_with_extra_attribute_in_cmd_raises_exception(
            self):
        with self.assertRaisesRegexp(
            utils.ValidationError,
            'The following extra attributes are present: invalid'):
            parameter_domain.PlatformParameterChange({
                'cmd': self.CMD_EDIT_RULES,
                'new_rules': [],
                'invalid': 'invalid'
            })

    def test_param_change_object_with_valid_data(self):
        param_change_object = (
            parameter_domain.PlatformParameterChange({
                'cmd': self.CMD_EDIT_RULES,
                'new_rules': []
            }))

        self.assertEqual(
            param_change_object.cmd, self.CMD_EDIT_RULES)
        self.assertEqual(
            param_change_object.new_rules, [])

    def test_to_dict(self):
        param_change_dict = {
            'cmd': self.CMD_EDIT_RULES,
            'new_rules': []
        }
        param_change_object = parameter_domain.PlatformParameterChange(
            param_change_dict)
        self.assertEqual(
            param_change_object.to_dict(),
            param_change_dict)


class EvaluationContextTests(test_utils.GenericTestBase):
    """Test for the EvaluationContext."""

    def test_create_feature_context_from_dict(self):
        context = parameter_domain.EvaluationContext.from_dict(
            {
                'client_type': 'Android',
                'browser_type': None,
                'app_version': '1.0.0',
                'user_locale': 'en',
            },
            {
                'server_mode': 'dev',
            },
        )
        self.assertEqual(context.client_type, 'Android')
        self.assertEqual(context.browser_type, None)
        self.assertEqual(context.app_version, '1.0.0')
        self.assertEqual(context.user_locale, 'en')
        self.assertEqual(context.server_mode, 'dev')

    def test_validate_passes_without_exception(self):
        context = parameter_domain.EvaluationContext.from_dict(
            {
                'client_type': 'Android',
                'browser_type': None,
                'app_version': '1.0.0',
                'user_locale': 'en',
            },
            {
                'server_mode': 'dev',
            },
        )
        context.validate()

    def test_validate_with_invalid_client_type_raises_exception(self):
        context = parameter_domain.EvaluationContext.from_dict(
            {
                'client_type': 'invalid',
                'browser_type': None,
                'app_version': '1.0.0',
                'user_locale': 'en',
            },
            {
                'server_mode': 'dev',
            },
        )
        with self.assertRaisesRegexp(
            utils.ValidationError, 'Invalid client type \'invalid\''):
            context.validate()

    def test_validate_with_invalid_browser_type_raises_exception(self):
        context = parameter_domain.EvaluationContext.from_dict(
            {
                'client_type': 'Web',
                'browser_type': 'Invalid',
                'app_version': '1.0.0',
                'user_locale': 'en',
            },
            {
                'server_mode': 'dev',
            },
        )
        with self.assertRaisesRegexp(
            utils.ValidationError, 'Invalid browser type \'Invalid\''):
            context.validate()

    def test_validate_with_invalid_app_version_raises_exception(self):
        context = parameter_domain.EvaluationContext.from_dict(
            {
                'client_type': 'Android',
                'browser_type': None,
                'app_version': 'a.a.a',
                'user_locale': 'en',
            },
            {
                'server_mode': 'dev',
            },
        )
        with self.assertRaisesRegexp(
            utils.ValidationError, 'Invalid version \'a.a.a\''):
            context.validate()

    def test_validate_with_invalid_user_locale_raises_exception(self):
        context = parameter_domain.EvaluationContext.from_dict(
            {
                'client_type': 'Android',
                'browser_type': None,
                'app_version': '1.0.0',
                'user_locale': 'invalid',
            },
            {
                'server_mode': 'dev',
            },
        )
        with self.assertRaisesRegexp(
            utils.ValidationError, 'Invalid user locale \'invalid\''):
            context.validate()

    def test_validate_with_invalid_server_mode_raises_exception(self):
        context = parameter_domain.EvaluationContext.from_dict(
            {
                'client_type': 'Android',
                'browser_type': None,
                'app_version': '1.0.0',
                'user_locale': 'en',
            },
            {
                'server_mode': 'invalid',
            },
        )
        with self.assertRaisesRegexp(
            utils.ValidationError, 'Invalid server mode \'invalid\''):
            context.validate()


class PlatformParameterFilterTests(test_utils.GenericTestBase):
    """Test for the PlatformParameterFilter."""

    def create_example_context(
            self, client_type='Android', browser_type=None, app_version='1.2.3',
            user_locale='en', mode='dev'):
        """Creates and returns an EvaluationContext using the given
        arguments.
        """
        return parameter_domain.EvaluationContext.from_dict(
            {
                'client_type': client_type,
                'browser_type': browser_type,
                'app_version': app_version,
                'user_locale': user_locale,
            },
            {
                'server_mode': mode,
            },
        )

    def test_create_filter_from_dict(self):
        filter_dict = {'type': 'app_version', 'conditions': [('=', '1.2.3')]}
        filter_domain = (
            parameter_domain
            .PlatformParameterFilter.from_dict(filter_dict))

        filter_domain.validate()

        self.assertEqual(filter_domain.type, 'app_version')
        self.assertEqual(filter_domain.conditions, [('=', '1.2.3')])

    def test_filter_to_dict(self):
        filter_dict = {'type': 'app_version', 'conditions': [('=', '1.2.3')]}
        filter_domain = (
            parameter_domain
            .PlatformParameterFilter.from_dict(filter_dict))

        self.assertEqual(filter_domain.to_dict(), filter_dict)

    def test_evaluate_server_mode_filter(self):
        filter_dict = {'type': 'server_mode', 'conditions': [('=', 'dev')]}
        filter_domain = (
            parameter_domain
            .PlatformParameterFilter.from_dict(filter_dict))

        dev_context = self.create_example_context(mode='dev')
        prod_context = self.create_example_context(mode='prod')

        self.assertTrue(filter_domain.evaluate(dev_context))
        self.assertFalse(filter_domain.evaluate(prod_context))

    def test_evaluate_user_locale_filter(self):
        filter_dict = {'type': 'user_locale', 'conditions': [('=', 'en')]}
        filter_domain = (
            parameter_domain
            .PlatformParameterFilter.from_dict(filter_dict))

        en_context = self.create_example_context(user_locale='en')
        zh_context = self.create_example_context(user_locale='zh-hans')

        self.assertTrue(filter_domain.evaluate(en_context))
        self.assertFalse(filter_domain.evaluate(zh_context))

    def test_evaluate_client_type_filter(self):
        filter_dict = {'type': 'client_type', 'conditions': [('=', 'Web')]}
        filter_domain = (
            parameter_domain
            .PlatformParameterFilter.from_dict(filter_dict))

        web_context = self.create_example_context(client_type='Web')
        native_context = self.create_example_context(client_type='Android')

        self.assertTrue(filter_domain.evaluate(web_context))
        self.assertFalse(filter_domain.evaluate(native_context))

    def test_evaluate_browser_type_filter(self):
        filter_dict = {'type': 'browser_type', 'conditions': [('=', 'Chrome')]}
        filter_domain = (
            parameter_domain
            .PlatformParameterFilter.from_dict(filter_dict))

        chrome_context = self.create_example_context(browser_type='Chrome')
        firefox_context = self.create_example_context(browser_type='Firefox')

        self.assertTrue(filter_domain.evaluate(chrome_context))
        self.assertFalse(filter_domain.evaluate(firefox_context))

    def test_evaluate_app_version_filter_with_eq_comparison(self):
        filter_dict = {'type': 'app_version', 'conditions': [('=', '1.2.3')]}
        filter_domain = (
            parameter_domain
            .PlatformParameterFilter.from_dict(filter_dict))
        self.assertTrue(filter_domain.evaluate(
            self.create_example_context(app_version='1.2.3')))
        self.assertFalse(filter_domain.evaluate(
            self.create_example_context(app_version='1.2.4')))

    def test_evaluate_app_version_filter_with_gt_comparison(self):
        filter_dict = {'type': 'app_version', 'conditions': [('>', '1.2.3')]}
        filter_domain = (
            parameter_domain
            .PlatformParameterFilter.from_dict(filter_dict))
        self.assertFalse(filter_domain.evaluate(
            self.create_example_context(app_version='0.2.3')))
        self.assertFalse(filter_domain.evaluate(
            self.create_example_context(app_version='1.1.2')))
        self.assertFalse(filter_domain.evaluate(
            self.create_example_context(app_version='1.2.3')))
        self.assertTrue(filter_domain.evaluate(
            self.create_example_context(app_version='1.2.4')))
        self.assertTrue(filter_domain.evaluate(
            self.create_example_context(app_version='1.3.0')))
        self.assertTrue(filter_domain.evaluate(
            self.create_example_context(app_version='2.0.0')))

    def test_evaluate_app_version_filter_with_gte_comparison(self):
        filter_dict = {'type': 'app_version', 'conditions': [('>=', '1.2.3')]}
        filter_domain = (
            parameter_domain
            .PlatformParameterFilter.from_dict(filter_dict))
        self.assertFalse(filter_domain.evaluate(
            self.create_example_context(app_version='0.2.3')))
        self.assertFalse(filter_domain.evaluate(
            self.create_example_context(app_version='1.1.2')))
        self.assertTrue(filter_domain.evaluate(
            self.create_example_context(app_version='1.2.3')))
        self.assertTrue(filter_domain.evaluate(
            self.create_example_context(app_version='1.2.4')))
        self.assertTrue(filter_domain.evaluate(
            self.create_example_context(app_version='1.3.0')))
        self.assertTrue(filter_domain.evaluate(
            self.create_example_context(app_version='2.0.0')))

    def test_evaluate_app_version_filter_with_lt_comparison(self):
        filter_dict = {'type': 'app_version', 'conditions': [('<', '1.2.3')]}
        filter_domain = (
            parameter_domain
            .PlatformParameterFilter.from_dict(filter_dict))
        self.assertTrue(filter_domain.evaluate(
            self.create_example_context(app_version='0.3.4')))
        self.assertTrue(filter_domain.evaluate(
            self.create_example_context(app_version='1.1.0')))
        self.assertTrue(filter_domain.evaluate(
            self.create_example_context(app_version='1.1.2')))
        self.assertTrue(filter_domain.evaluate(
            self.create_example_context(app_version='1.2.2')))
        self.assertFalse(filter_domain.evaluate(
            self.create_example_context(app_version='1.2.3')))
        self.assertFalse(filter_domain.evaluate(
            self.create_example_context(app_version='1.2.4')))
        self.assertFalse(filter_domain.evaluate(
            self.create_example_context(app_version='1.3.0')))
        self.assertFalse(filter_domain.evaluate(
            self.create_example_context(app_version='1.10.0')))
        self.assertFalse(filter_domain.evaluate(
            self.create_example_context(app_version='2.0.0')))

    def test_evaluate_app_version_filter_with_lte_comparison(self):
        filter_dict = {'type': 'app_version', 'conditions': [('<=', '1.2.3')]}
        filter_domain = (
            parameter_domain
            .PlatformParameterFilter.from_dict(filter_dict))
        self.assertTrue(filter_domain.evaluate(
            self.create_example_context(app_version='0.3.4')))
        self.assertTrue(filter_domain.evaluate(
            self.create_example_context(app_version='1.1.0')))
        self.assertTrue(filter_domain.evaluate(
            self.create_example_context(app_version='1.2.2')))
        self.assertTrue(filter_domain.evaluate(
            self.create_example_context(app_version='1.2.3')))
        self.assertFalse(filter_domain.evaluate(
            self.create_example_context(app_version='1.2.4')))
        self.assertFalse(filter_domain.evaluate(
            self.create_example_context(app_version='1.3.0')))
        self.assertFalse(filter_domain.evaluate(
            self.create_example_context(app_version='1.10.0')))
        self.assertFalse(filter_domain.evaluate(
            self.create_example_context(app_version='2.0.0')))

    def test_evaluate_filter_with_multiple_values(self):
        filter_dict = {
            'type': 'server_mode',
            'conditions': [('=', 'dev'), ('=', 'prod')]
        }
        filter_domain = (
            parameter_domain
            .PlatformParameterFilter.from_dict(filter_dict))
        filter_domain.validate()

        dev_context = self.create_example_context(mode='dev')
        test_context = self.create_example_context(mode='test')
        prod_context = self.create_example_context(mode='prod')

        self.assertTrue(filter_domain.evaluate(dev_context))
        self.assertTrue(filter_domain.evaluate(prod_context))
        self.assertFalse(filter_domain.evaluate(test_context))

    def test_evaluate_app_version_filter_with_multiple_values(self):
        filter_dict = {
            'type': 'app_version',
            'conditions': [('=', '1.2.3'), ('=', '1.2.4')]
        }
        filter_domain = (
            parameter_domain
            .PlatformParameterFilter.from_dict(filter_dict))
        filter_domain.validate()

        self.assertTrue(filter_domain.evaluate(
            self.create_example_context(app_version='1.2.3')))
        self.assertTrue(filter_domain.evaluate(
            self.create_example_context(app_version='1.2.4')))
        self.assertFalse(filter_domain.evaluate(
            self.create_example_context(app_version='1.5.3')))

    def test_evaluate_app_version_filter_with_no_version_in_context(self):
        filter_dict = {
            'type': 'app_version',
            'conditions': [('=', '1.2.3'), ('=', '1.2.4')]
        }
        filter_domain = parameter_domain.PlatformParameterFilter.from_dict(
            filter_dict)

        self.assertFalse(filter_domain.evaluate(
            self.create_example_context(app_version=None)))

    def test_evaluate_filter_with_unsupported_operation_raises_exception(self):
        filter_domain = (
            parameter_domain
            .PlatformParameterFilter.from_dict(
                {'type': 'server_mode', 'conditions': [('!=', 'dev')]}
            ))
        with self.assertRaisesRegexp(
            Exception, 'Unsupported comparison operator \'!=\''):
            filter_domain.evaluate(self.create_example_context())

    def test_validate_filter_passes_without_exception(self):
        filter_dict = {
            'type': 'server_mode',
            'conditions': [('=', 'dev'), ('=', 'prod')]
        }
        filter_domain = (
            parameter_domain
            .PlatformParameterFilter.from_dict(filter_dict))
        filter_domain.validate()

    def test_validate_filter_with_invalid_type_raises_exception(self):
        filter_domain = (
            parameter_domain
            .PlatformParameterFilter.from_dict(
                {'type': 'invalid', 'conditions': [('=', 'value1')]}
            ))
        with self.assertRaisesRegexp(
            utils.ValidationError, 'Unsupported filter type \'invalid\''):
            filter_domain.validate()

    def test_validate_filter_with_unsupported_operation_raises_exception(self):
        filter_domain = (
            parameter_domain
            .PlatformParameterFilter.from_dict(
                {'type': 'server_mode', 'conditions': [('!=', 'dev')]}
            ))
        with self.assertRaisesRegexp(
            utils.ValidationError, 'Unsupported comparison operator \'!=\''):
            filter_domain.validate()

    def test_validate_filter_with_invalid_server_mode_raises_exception(self):
        filter_domain = (
            parameter_domain
            .PlatformParameterFilter.from_dict(
                {'type': 'server_mode', 'conditions': [('=', 'invalid')]}
            ))
        with self.assertRaisesRegexp(
            utils.ValidationError, 'Invalid server mode \'invalid\''):
            filter_domain.validate()

    def test_validate_filter_with_invalid_user_locale_raises_exception(self):
        filter_domain = (
            parameter_domain
            .PlatformParameterFilter.from_dict(
                {'type': 'user_locale', 'conditions': [('=', 'invalid')]}
            ))
        with self.assertRaisesRegexp(
            utils.ValidationError, 'Invalid user locale \'invalid\''):
            filter_domain.validate()

    def test_validate_filter_with_invalid_client_type_raises_exception(self):
        filter_domain = (
            parameter_domain
            .PlatformParameterFilter.from_dict(
                {'type': 'client_type', 'conditions': [('=', 'invalid')]}
            ))
        with self.assertRaisesRegexp(
            utils.ValidationError, 'Invalid client type \'invalid\''):
            filter_domain.validate()

    def test_validate_filter_with_invalid_version_expr_raises_exception(self):
        filter_domain = (
            parameter_domain
            .PlatformParameterFilter.from_dict(
                {'type': 'app_version', 'conditions': [('=', '1.a.2')]}
            ))

        with self.assertRaisesRegexp(
            utils.ValidationError, 'Invalid version expression \'1.a.2\''):
            filter_domain.validate()


class PlatformParameterRuleTests(test_utils.GenericTestBase):
    """Test for the PlatformParameterRule."""

    def test_from_dict(self):
        filters = [
            {
                'type': 'app_version',
                'conditions': [('=', '1.2.3')]
            },
            {
                'type': 'server_mode',
                'conditions': [('=', 'dev'), ('=', 'test')]
            }
        ]
        rule = parameter_domain.PlatformParameterRule.from_dict(
            {
                'filters': filters,
                'value_when_matched': False,
            },
            feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION
        )
        self.assertIsInstance(rule, parameter_domain.PlatformParameterRule)

        filter_domain = rule.filters[0]
        self.assertIsInstance(
            filter_domain, parameter_domain.PlatformParameterFilter)
        self.assertEqual(len(rule.filters), 2)
        self.assertEqual(filter_domain.type, 'app_version')
        self.assertEqual(filter_domain.conditions, [('=', '1.2.3')])
        self.assertEqual(rule.value_when_matched, False)

    def test_from_dict_with_old_schema_version_failure(self):
        filters = [{'type': 'app_version', 'conditions': [('=', '1.2.3')]}]
        with self.swap(
            feconf, 'CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION', 2):
            with self.assertRaisesRegexp(
                Exception, 'rule schema version to be 2'):
                parameter_domain.PlatformParameterRule.from_dict(
                    {
                        'filters': filters,
                        'value_when_matched': False,
                    },
                    1,
                )

    def test_to_dict(self):
        rule_dict = {
            'filters': [
                {
                    'type': 'app_version',
                    'conditions': [('=', '1.2.3')]
                }
            ],
            'value_when_matched': False,
        }
        rule = parameter_domain.PlatformParameterRule.from_dict(
            rule_dict,
            feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION
        )
        self.assertEqual(rule.to_dict(), rule_dict)

    def test_has_server_mode_filter(self):
        rule = parameter_domain.PlatformParameterRule.from_dict(
            {
                'filters': [
                    {'type': 'app_version', 'conditions': [('=', '1.2.3')]}
                ],
                'value_when_matched': False,
            },
            feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION
        )
        self.assertFalse(rule.has_server_mode_filter())

        rule = parameter_domain.PlatformParameterRule.from_dict(
            {
                'filters': [
                    {'type': 'server_mode', 'conditions': [('=', 'dev')]}
                ],
                'value_when_matched': False,
            },
            feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION
        )
        self.assertTrue(rule.has_server_mode_filter())

    def test_evaluation_matched(self):
        rule = parameter_domain.PlatformParameterRule.from_dict(
            {
                'filters': [
                    {'type': 'app_version', 'conditions': [('=', '1.2.3')]},
                    {'type': 'user_locale', 'conditions': [('=', 'en')]},
                ],
                'value_when_matched': 'matched_val',
            },
            feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION
        )
        context = parameter_domain.EvaluationContext.from_dict(
            {
                'client_type': 'Android',
                'browser_type': None,
                'app_version': '1.2.3',
                'user_locale': 'en',
            },
            {
                'server_mode': 'dev',
            },
        )
        self.assertTrue(rule.evaluate(context))

    def test_evaluation_not_matched(self):
        rule = parameter_domain.PlatformParameterRule.from_dict(
            {
                'filters': [
                    {'type': 'app_version', 'conditions': [('=', '1.2.3')]},
                    {'type': 'user_locale', 'conditions': [('=', 'en-UK')]},
                ],
                'value_when_matched': 'matched_val',
            },
            feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION
        )
        context = parameter_domain.EvaluationContext.from_dict(
            {
                'client_type': 'Android',
                'browser_type': None,
                'app_version': '1.2.3',
                'user_locale': 'en',
            },
            {
                'server_mode': 'dev',
            },
        )
        self.assertFalse(rule.evaluate(context))

    def test_validate_each_filter(self):
        filters = [
            {'type': 'app_version', 'conditions': [('=', '1.2.3')]},
            {'type': 'invalid', 'conditions': [('=', '1.2.3')]},
        ]
        rule = parameter_domain.PlatformParameterRule.from_dict(
            {
                'filters': filters,
                'value_when_matched': False,
            },
            feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION
        )
        with self.assertRaisesRegexp(
            utils.ValidationError, 'Unsupported filter type \'invalid\''):
            rule.validate()


class PlatformParameterMetadataTests(test_utils.GenericTestBase):
    """Test for the PlatformParameterMetadata."""

    def test_from_dict(self):
        metadata = parameter_domain.PlatformParameterMetadata.from_dict(
            {'is_feature': True, 'feature_stage': 'dev'})

        self.assertTrue(metadata.is_feature)
        self.assertEqual(metadata.feature_stage, 'dev')

    def test_to_dict(self):
        metadata_dict = {
            'is_feature': True,
            'feature_stage': 'dev',
        }
        metadata = parameter_domain.PlatformParameterMetadata.from_dict(
            metadata_dict)

        self.assertDictEqual(metadata.to_dict(), metadata_dict)


class PlatformParameterTests(test_utils.GenericTestBase):
    """Test for the PlatformParameter."""

    def test_from_dict(self):
        param = parameter_domain.PlatformParameter.from_dict({
            'name': 'parameter_a',
            'description': 'for test',
            'data_type': 'string',
            'rules': [
                {
                    'filters': [
                        {
                            'type': 'server_mode',
                            'conditions': [('=', 'dev')]
                        }
                    ],
                    'value_when_matched': '222'
                }
            ],
            'rule_schema_version': (
                feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION),
            'default_value': '333',
            'metadata': {
                'is_feature': False,
                'feature_stage': None,
            },
        })

        self.assertIsInstance(param, parameter_domain.PlatformParameter)
        self.assertEqual(param.name, 'parameter_a')
        self.assertEqual(param.description, 'for test')
        self.assertEqual(param.data_type, 'string')
        self.assertEqual(len(param.rules), 1)
        self.assertIsInstance(
            param.metadata, parameter_domain.PlatformParameterMetadata)
        self.assertEqual(param.default_value, '333')
        self.assertEqual(
            param.rule_schema_version,
            feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION)

    def test_validate_with_invalid_name_raises_exception(self):
        param = parameter_domain.PlatformParameter.from_dict({
            'name': 'Invalid~Name',
            'description': 'for test',
            'data_type': 'string',
            'rules': [
                {
                    'filters': [
                        {
                            'type': 'server_mode',
                            'conditions': [('=', 'dev')]
                        }
                    ],
                    'value_when_matched': '222'
                }
            ],
            'rule_schema_version': (
                feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION),
            'default_value': '333',
            'metadata': {
                'is_feature': False,
                'feature_stage': None,
            },
        })
        with self.assertRaisesRegexp(
            utils.ValidationError,
            'Invalid parameter name \'%s\'' % param.name):
            param.validate()

        param1 = parameter_domain.PlatformParameter.from_dict({
            'name': 'parameter.name',
            'description': 'for test',
            'data_type': 'string',
            'rules': [
                {
                    'filters': [
                        {
                            'type': 'server_mode',
                            'conditions': [('=', 'dev')]
                        }
                    ],
                    'value_when_matched': '222'
                }
            ],
            'rule_schema_version': (
                feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION),
            'default_value': '333',
            'metadata': {
                'is_feature': False,
                'feature_stage': None,
            },
        })
        with self.assertRaisesRegexp(
            utils.ValidationError,
            'Invalid parameter name \'%s\'' % param1.name):
            param1.validate()

    def test_validate_with_long_name_raises_exception(self):
        long_name = 'Long_' * 50 + 'Name'
        param = parameter_domain.PlatformParameter.from_dict({
            'name': long_name,
            'description': 'for test',
            'data_type': 'string',
            'rules': [
                {
                    'filters': [
                        {
                            'type': 'server_mode',
                            'conditions': [('=', 'dev')]
                        }
                    ],
                    'value_when_matched': '222'
                }
            ],
            'rule_schema_version': (
                feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION),
            'default_value': '333',
            'metadata': {
                'is_feature': False,
                'feature_stage': None,
            },
        })
        with self.assertRaisesRegexp(
            utils.ValidationError,
            'Invalid parameter name \'%s\'' % long_name):
            param.validate()

    def test_validate_with_unsupported_data_type_raises_exception(self):
        param = parameter_domain.PlatformParameter.from_dict({
            'name': 'parameter_a',
            'description': 'for test',
            'data_type': 'InvalidType',
            'rules': [
                {
                    'filters': [
                        {
                            'type': 'server_mode',
                            'conditions': [('=', 'dev')]
                        }
                    ],
                    'value_when_matched': '222'
                }
            ],
            'rule_schema_version': (
                feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION),
            'default_value': '333',
            'metadata': {
                'is_feature': False,
                'feature_stage': None,
            },
        })
        with self.assertRaisesRegexp(
            utils.ValidationError, 'Unsupported data type \'InvalidType\''):
            param.validate()

    def test_validate_with_inconsistent_data_type_in_rules_raises_exception(
            self):
        param = parameter_domain.PlatformParameter.from_dict({
            'name': 'parameter_a',
            'description': 'for test',
            'data_type': 'bool',
            'rules': [
                {
                    'filters': [
                        {
                            'type': 'server_mode',
                            'conditions': [('=', 'dev')]
                        }
                    ],
                    'value_when_matched': '222'
                },
            ],
            'rule_schema_version': (
                feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION),
            'default_value': False,
            'metadata': {
                'is_feature': False,
                'feature_stage': None,
            },
        })
        with self.assertRaisesRegexp(
            utils.ValidationError,
            'Expected bool, received \'222\' in value_when_matched'):
            param.validate()

    def test_validate_with_inconsistent_default_value_type_raises_exception(
            self):
        param = parameter_domain.PlatformParameter.from_dict({
            'name': 'parameter_a',
            'description': 'for test',
            'data_type': 'bool',
            'rules': [],
            'rule_schema_version': (
                feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION),
            'default_value': '111',
            'metadata': {
                'is_feature': False,
                'feature_stage': None,
            },
        })
        with self.assertRaisesRegexp(
            utils.ValidationError,
            'Expected bool, received \'111\' in default value'):
            param.validate()

    def test_to_dict(self):
        param_dict = {
            'name': 'parameter_a',
            'description': 'for test',
            'data_type': 'string',
            'rules': [
                {
                    'filters': [
                        {
                            'type': 'server_mode',
                            'conditions': [('=', 'dev')]
                        }
                    ],
                    'value_when_matched': '222'
                }
            ],
            'rule_schema_version': (
                feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION),
            'default_value': '333',
            'metadata': {
                'is_feature': False,
                'feature_stage': None
            }
        }
        parameter = parameter_domain.PlatformParameter.from_dict(param_dict)
        self.assertDictEqual(parameter.to_dict(), param_dict)

    def test_evaluate_in_dev(self):
        parameter = parameter_domain.PlatformParameter.from_dict({
            'name': 'parameter_a',
            'description': 'for test',
            'data_type': 'string',
            'rules': [
                {
                    'filters': [
                        {
                            'type': 'server_mode',
                            'conditions': [('=', 'dev')]
                        }
                    ],
                    'value_when_matched': '222'
                }
            ],
            'rule_schema_version': (
                feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION),
            'default_value': '333',
            'metadata': {
                'is_feature': False,
                'feature_stage': None,
            },
        })

        dev_context = parameter_domain.EvaluationContext.from_dict(
            {
                'client_type': 'Android',
                'browser_type': None,
                'app_version': '1.2.3',
                'user_locale': 'en',
            },
            {
                'server_mode': 'dev',
            },
        )
        self.assertEqual(parameter.evaluate(dev_context), '222')

    def test_evaluate_in_prod(self):
        parameter = parameter_domain.PlatformParameter.from_dict({
            'name': 'parameter_a',
            'description': 'for test',
            'data_type': 'string',
            'rules': [
                {
                    'filters': [
                        {
                            'type': 'server_mode',
                            'conditions': [('=', 'dev')]
                        }
                    ],
                    'value_when_matched': '222'
                }
            ],
            'rule_schema_version': (
                feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION),
            'default_value': '111',
            'metadata': {
                'is_feature': False,
                'feature_stage': None,
            },
        })

        prod_context = parameter_domain.EvaluationContext.from_dict(
            {
                'client_type': 'Android',
                'browser_type': None,
                'app_version': '1.2.3',
                'user_locale': 'en',
            },
            {
                'server_mode': 'prod',
            },
        )
        self.assertEqual(parameter.evaluate(prod_context), '111')

    def test_validate_feature(self):
        parameter = parameter_domain.PlatformParameter.from_dict({
            'name': 'parameter_a',
            'description': 'for test',
            'data_type': 'bool',
            'rules': [
                {
                    'filters': [
                        {'type': 'server_mode', 'conditions': [('=', 'dev')]}
                    ],
                    'value_when_matched': False
                }
            ],
            'rule_schema_version': (
                feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION),
            'default_value': False,
            'metadata': {
                'is_feature': True,
                'feature_stage': 'dev',
            }
        })
        parameter.validate()

    def test_validate_feature_with_invalid_type_raises_exception(self):
        parameter = parameter_domain.PlatformParameter.from_dict({
            'name': 'parameter_a',
            'description': 'for test',
            'data_type': 'string',
            'rules': [],
            'rule_schema_version': (
                feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION),
            'default_value': '111',
            'metadata': {
                'is_feature': True,
                'feature_stage': 'dev',
            }
        })
        with self.assertRaisesRegexp(
            utils.ValidationError,
            'Data type of feature flags must be bool, got \'string\' instead'):
            parameter.validate()

    def test_validate_feature_with_invalid_stage_raises_exception(self):
        parameter = parameter_domain.PlatformParameter.from_dict({
            'name': 'parameter_a',
            'description': 'for test',
            'data_type': 'bool',
            'rules': [],
            'rule_schema_version': (
                feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION),
            'default_value': False,
            'metadata': {
                'is_feature': True,
                'feature_stage': 'Invalid',
            }
        })
        with self.assertRaisesRegexp(
            utils.ValidationError, 'Invalid feature stage, got \'Invalid\''):
            parameter.validate()

    def test_validate_feature_with_no_mode_filter_raises_exception(self):
        parameter = parameter_domain.PlatformParameter.from_dict({
            'name': 'parameter_a',
            'description': 'for test',
            'data_type': 'bool',
            'rules': [
                {
                    'filters': [],
                    'value_when_matched': True
                }
            ],
            'rule_schema_version': (
                feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION),
            'default_value': False,
            'metadata': {
                'is_feature': True,
                'feature_stage': 'dev',
            }
        })
        with self.assertRaisesRegexp(
            utils.ValidationError, 'must have a server_mode filter'):
            parameter.validate()

    def test_validate_dev_feature_for_inappropriate_env_raises_exception(self):
        parameter = parameter_domain.PlatformParameter.from_dict({
            'name': 'parameter_a',
            'description': 'for test',
            'data_type': 'bool',
            'rules': [
                {
                    'filters': [
                        {'type': 'server_mode', 'conditions': [('=', 'test')]}],
                    'value_when_matched': True
                }
            ],
            'rule_schema_version': (
                feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION),
            'default_value': False,
            'metadata': {
                'is_feature': True,
                'feature_stage': 'dev',
            }
        })
        with self.assertRaisesRegexp(
            utils.ValidationError, 'cannot be enabled in test'):
            parameter.validate()

    def test_validate_test_feature_for_inappropriate_env_raises_exception(
            self):
        parameter = parameter_domain.PlatformParameter.from_dict({
            'name': 'parameter_a',
            'description': 'for test',
            'data_type': 'bool',
            'rules': [
                {
                    'filters': [
                        {'type': 'server_mode', 'conditions': [('=', 'prod')]}],
                    'value_when_matched': True
                }
            ],
            'rule_schema_version': (
                feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION),
            'default_value': False,
            'metadata': {
                'is_feature': True,
                'feature_stage': 'test',
            }
        })
        with self.assertRaisesRegexp(
            utils.ValidationError, 'cannot be enabled in production'):
            parameter.validate()


class PlatformParameterRegistryTests(test_utils.GenericTestBase):
    """Tests for the platform parameter Registry."""

    def setUp(self):
        super(PlatformParameterRegistryTests, self).setUp()

        self.original_param_registry = (
            parameter_domain.Registry.parameter_registry)
        parameter_domain.Registry.parameter_registry.clear()

        # Parameter names that might be used in following tests.
        parameter_names = ('parameter_a', 'parameter_b')
        memcache_keys = [
            parameter_domain.PlatformParameter.get_memcache_key(name)
            for name in parameter_names]
        memcache_services.delete_multi(memcache_keys)

    def tearDown(self):
        super(PlatformParameterRegistryTests, self).tearDown()

        parameter_domain.Registry.parameter_registry = (
            self.original_param_registry)

    def create_example_parameter_with_name(self, name):
        """Creates and returns an example parameter with the given name."""
        parameter_domain.Registry.create_platform_parameter_from_dict({
            'name': name,
            'description': 'for test',
            'data_type': 'string',
            'rules': [
                {
                    'filters': [
                        {
                            'type': 'server_mode',
                            'conditions': [('=', 'dev')]
                        }
                    ],
                    'value_when_matched': '222'
                }
            ],
            'rule_schema_version': (
                feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION),
            'default_value': '111',
            'metadata': {
                'is_feature': False,
                'feature_stage': None,
            },
        })

    def test_create_platform_parameter(self):
        parameter = parameter_domain.Registry.create_platform_parameter(
            'parameter_a', 'test', 'bool')
        self.assertIsInstance(parameter, parameter_domain.PlatformParameter)
        parameter.validate()

    def test_create_platform_parameter_with_invalid_type_failure(self):
        with self.assertRaisesRegexp(
            Exception, 'Unsupported data type \'Invalid\''):
            parameter_domain.Registry.create_platform_parameter(
                'parameter_a', 'test', 'Invalid')

    def test_create_feature_flag(self):
        feature = parameter_domain.Registry.create_feature_flag(
            'parameter_a', 'test', 'dev')
        self.assertEqual(feature.data_type, 'bool')
        self.assertTrue(feature.metadata.is_feature)
        self.assertEqual(feature.metadata.feature_stage, 'dev')
        feature.validate()

    def test_default_value_of_bool_platform_parameter(self):
        parameter = parameter_domain.Registry.create_platform_parameter(
            'parameter_a', 'test', 'bool')
        parameter.validate()
        self.assertEqual(parameter.default_value, False)

    def test_default_value_of_string_platform_parameter(self):
        parameter = parameter_domain.Registry.create_platform_parameter(
            'parameter_a', 'test', 'string')
        parameter.validate()
        self.assertEqual(parameter.default_value, '')

    def test_default_value_of_int_platform_parameter(self):
        parameter = parameter_domain.Registry.create_platform_parameter(
            'parameter_a', 'test', 'number')
        parameter.validate()
        self.assertEqual(parameter.default_value, 0)

    def test_create_and_get_platform_parameter(self):
        parameter_name = 'parameter_a'
        self.create_example_parameter_with_name(parameter_name)
        parameter = parameter_domain.Registry.get_platform_parameter(
            parameter_name)
        self.assertIsNotNone(parameter)
        self.assertIsInstance(parameter, parameter_domain.PlatformParameter)
        # Get from memcache.
        self.assertIsNotNone(
            parameter_domain.Registry.get_platform_parameter(
                parameter_name))

    def test_create_platform_parameter_with_the_same_name_failure(self):
        param_name = 'parameter_a'
        self.create_example_parameter_with_name(param_name)
        with self.assertRaisesRegexp(
            Exception, 'Parameter with name %s already exists' % param_name):
            self.create_example_parameter_with_name(param_name)

    def test_get_non_existing_parameter_failure(self):
        with self.assertRaisesRegexp(Exception, 'not found'):
            parameter_domain.Registry.get_platform_parameter('parameter_a')

    def test_get_all_parameter_names(self):
        parameter_names = ['parameter_a', 'parameter_b']
        for parameter_name in parameter_names:
            self.create_example_parameter_with_name(parameter_name)
        self.assertEqual(
            sorted(
                parameter_domain.Registry.get_all_platform_parameter_names()),
            sorted(parameter_names))

    def test_memcache_is_set_after_getting(self):
        parameter_name = 'parameter_a'
        self.create_example_parameter_with_name(parameter_name)

        self.assertIsNone(
            parameter_domain.Registry.load_platform_parameter_from_memcache(
                parameter_name))
        parameter_domain.Registry.get_platform_parameter(parameter_name)
        self.assertIsNotNone(
            parameter_domain.Registry.load_platform_parameter_from_memcache(
                parameter_name))

    def test_update_parameter(self):
        parameter_name = 'parameter_a'
        self.create_example_parameter_with_name(parameter_name)

        parameter_domain.Registry.update_platform_parameter(
            parameter_name,
            feconf.SYSTEM_COMMITTER_ID,
            'commit message',
            [
                {
                    'filters': [
                        {'type': 'server_mode', 'conditions': [('=', 'dev')]}
                    ],
                    'value_when_matched': 'updated'
                }
            ],
        )
        # Cached value is invalidated after update.
        self.assertIsNone(
            parameter_domain.Registry.load_platform_parameter_from_memcache(
                parameter_name))
        parameter_updated = parameter_domain.Registry.get_platform_parameter(
            parameter_name)

        self.assertEqual(parameter_updated.name, parameter_name)
        self.assertEqual(len(parameter_updated.rules), 1)
        self.assertEqual(
            parameter_updated.rules[0].value_when_matched, 'updated')

        self.assertIsNotNone(
            parameter_domain.Registry.load_platform_parameter_from_memcache(
                parameter_name))

    def test_update_parameter_with_invalid_rules_failure(self):
        parameter_name = 'parameter_a'
        self.create_example_parameter_with_name(parameter_name)

        param = parameter_domain.Registry.get_platform_parameter(
            parameter_name)
        param.validate()

        with self.assertRaisesRegexp(
            utils.ValidationError, 'Expected string'):
            parameter_domain.Registry.update_platform_parameter(
                parameter_name,
                feconf.SYSTEM_COMMITTER_ID,
                'commit message',
                [
                    {
                        'filters': [
                            {
                                'type': 'server_mode',
                                'conditions': [('=', 'dev')]
                            }
                        ],
                        'value_when_matched': True
                    }
                ],
            )

    def test_updated_parameter_is_saved_in_storage(self):
        parameter_name = 'parameter_a'
        self.create_example_parameter_with_name(parameter_name)
        self.assertIsNone(
            parameter_domain.Registry.load_platform_parameter_from_storage(
                parameter_name))

        parameter_domain.Registry.update_platform_parameter(
            parameter_name,
            feconf.SYSTEM_COMMITTER_ID,
            'commit message',
            [
                {
                    'filters': [
                        {'type': 'server_mode', 'conditions': [('=', 'dev')]}
                    ],
                    'value_when_matched': 'updated'
                }
            ],
        )

        parameter_updated = (
            parameter_domain
            .Registry
            .load_platform_parameter_from_storage(parameter_name)
        )
        self.assertIsNotNone(parameter_updated)

    def test_evaluate_all_parameters(self):
        context = parameter_domain.EvaluationContext.from_dict(
            {
                'client_type': 'Android',
                'browser_type': None,
                'app_version': '1.2.3',
                'user_locale': 'en',
            },
            {
                'server_mode': 'dev',
            },
        )
        parameter_domain.Registry.create_platform_parameter_from_dict({
            'name': 'parameter_a',
            'description': 'for test',
            'data_type': 'string',
            'rules': [
                {
                    'filters': [
                        {
                            'type': 'server_mode',
                            'conditions': [('=', 'dev')]
                        }
                    ],
                    'value_when_matched': '222'
                }
            ],
            'rule_schema_version': (
                feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION),
            'default_value': '333',
            'metadata': {
                'is_feature': True,
                'feature_stage': 'in-dev',
            }
        })
        parameter_domain.Registry.create_platform_parameter_from_dict({
            'name': 'parameter_b',
            'description': 'for test',
            'data_type': 'bool',
            'rules': [],
            'rule_schema_version': (
                feconf.CURRENT_PLATFORM_PARAMETER_RULE_SCHEMA_VERSION),
            'default_value': False,
            'metadata': {
                'is_feature': False,
                'feature_stage': None,
            },
        })

        self.assertDictEqual(
            parameter_domain.Registry.evaluate_all_platform_parameters(context),
            {
                'parameter_a': '222',
                'parameter_b': False,
            }
        )

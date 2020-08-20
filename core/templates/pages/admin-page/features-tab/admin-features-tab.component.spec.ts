// Copyright 2020 The Oppia Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS-IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * @fileoverview Unit tests for the feature tab in admin page.
 */

import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, fakeAsync, async, TestBed, flushMicrotasks } from
  '@angular/core/testing';
import { FormsModule } from '@angular/forms';

import { cloneDeep } from 'lodash';

import { AdminPageData } from 'domain/admin/admin-backend-api.service';
import { AdminFeaturesTabComponent } from
  'pages/admin-page/features-tab/admin-features-tab.component';
import { AdminDataService } from 'pages/admin-page/services/admin-data.service';
import { AdminTaskManagerService } from
  'pages/admin-page/services/admin-task-manager.service';
import { PlatformFeatureAdminBackendApiService } from
  'domain/platform_feature/platform-feature-admin-backend-api.service';
import { PlatformParameterFilterType, ServerMode } from
  'domain/platform_feature/platform-parameter-filter-object.factory';
import { PlatformParameterObjectFactory, FeatureStage, PlatformParameter } from
  'domain/platform_feature/platform-parameter-object.factory';
import { WindowRef } from 'services/contextual/window-ref.service';

describe('Admin page feature tab', function() {
  let component: AdminFeaturesTabComponent;
  let fixture: ComponentFixture<AdminFeaturesTabComponent>;

  let paramFactory: PlatformParameterObjectFactory;
  let adminDataService: AdminDataService;
  let featureApiService: PlatformFeatureAdminBackendApiService;
  let adminTaskManagerService: AdminTaskManagerService;
  let windowRef: WindowRef;

  let updateApiSpy: jasmine.Spy;

  let mockConfirmResult: (val: boolean) => void;
  let mockPromptResult: (msg: string) => void;

  beforeEach(async(() => {
    TestBed
      .configureTestingModule({
        imports: [FormsModule, HttpClientTestingModule],
        declarations: [AdminFeaturesTabComponent],
      })
      .compileComponents();

    fixture = TestBed.createComponent(AdminFeaturesTabComponent);
    component = fixture.componentInstance;

    paramFactory = TestBed.get(PlatformParameterObjectFactory);
    adminDataService = TestBed.get(AdminDataService);
    featureApiService = TestBed.get(PlatformFeatureAdminBackendApiService);
    windowRef = TestBed.get(WindowRef);
    adminTaskManagerService = TestBed.get(AdminTaskManagerService);

    let confirmResult = true;
    let promptResult = 'mock msg';
    spyOnProperty(windowRef, 'nativeWindow').and.returnValue({
      confirm: () => confirmResult,
      prompt: () => promptResult
    });
    mockConfirmResult = val => confirmResult = val;
    mockPromptResult = msg => promptResult = msg;

    spyOn(adminDataService, 'getDataAsync').and.resolveTo(<AdminPageData>{
      featureFlags: [
        paramFactory.createFromBackendDict({
          data_type: 'bool',
          default_value: false,
          description: 'This is a dummy feature flag.',
          feature_stage: FeatureStage.DEV,
          is_feature: true,
          name: 'dummy_feature',
          rule_schema_version: 1,
          rules: [{
            filters: [
              {
                type: PlatformParameterFilterType.ServerMode,
                conditions: [['=', ServerMode.Dev]]
              }
            ],
            // This does not match the data type of feature flags, but this is
            // intended as string values are more suitable for identifying rules
            // in the following tests.
            value_when_matched: 'original',
          }],
        })
      ]
    });

    updateApiSpy = spyOn(featureApiService, 'updateFeatureFlag')
      .and.resolveTo(null);

    component.ngOnInit();
  }));

  it('should load feature flags on init', () => {
    expect(component.featureFlags.length).toBe(1);
    expect(component.featureFlags[0].name).toEqual('dummy_feature');
  });

  describe('.addNewRuleToTop', () => {
    it('should add new rule to top of rule list', () => {
      const featureFlag = component.featureFlags[0];

      expect(featureFlag.rules.length).toBe(1);

      component.addNewRuleToTop(featureFlag);
      expect(featureFlag.rules.length).toBe(2);
      expect(featureFlag.rules[1].valueWhenMatched).toEqual('original');
    });
  });

  describe('.addNewRuleToBottom', () => {
    it('should add new rule to bottom of rule list', () => {
      const featureFlag = component.featureFlags[0];

      expect(featureFlag.rules.length).toBe(1);

      component.addNewRuleToBottom(featureFlag);
      expect(featureFlag.rules.length).toBe(2);
      expect(featureFlag.rules[0].valueWhenMatched).toEqual('original');
    });
  });

  describe('.removeRule', () => {
    it('should remove rule', () => {
      const featureFlag = component.featureFlags[0];
      component.addNewRuleToBottom(featureFlag);
      featureFlag.rules[1].valueWhenMatched = '1';

      component.removeRule(featureFlag, 0);

      expect(featureFlag.rules.length).toBe(1);
      expect(featureFlag.rules[0].valueWhenMatched).toEqual('1');
    });
  });

  describe('.moveRuleUp', () => {
    it('should move rule up', () => {
      const featureFlag = component.featureFlags[0];
      component.addNewRuleToBottom(featureFlag);
      featureFlag.rules[1].valueWhenMatched = '1';
      component.addNewRuleToBottom(featureFlag);
      featureFlag.rules[2].valueWhenMatched = '2';

      component.moveRuleUp(featureFlag, 1);

      expect(featureFlag.rules[0].valueWhenMatched).toEqual('1');
      expect(featureFlag.rules[1].valueWhenMatched).toEqual('original');
      expect(featureFlag.rules[2].valueWhenMatched).toEqual('2');
    });
  });

  describe('.moveRuleDown', () => {
    it('should move rule down', () => {
      const featureFlag = component.featureFlags[0];
      component.addNewRuleToBottom(featureFlag);
      featureFlag.rules[1].valueWhenMatched = '1';
      component.addNewRuleToBottom(featureFlag);
      featureFlag.rules[2].valueWhenMatched = '2';

      component.moveRuleDown(featureFlag, 1);

      expect(featureFlag.rules[0].valueWhenMatched).toEqual('original');
      expect(featureFlag.rules[1].valueWhenMatched).toEqual('2');
      expect(featureFlag.rules[2].valueWhenMatched).toEqual('1');
    });
  });

  describe('.addNewFilter', () => {
    it('should add new filter', () => {
      const rule = component.featureFlags[0].rules[0];

      expect(rule.filters.length).toBe(1);

      component.addNewFilter(rule);
      rule.filters[1].type = PlatformParameterFilterType.UserLocale;

      expect(rule.filters.length).toBe(2);
      expect(rule.filters[0].type)
        .toEqual(PlatformParameterFilterType.ServerMode);
      expect(rule.filters[1].type)
        .toEqual(PlatformParameterFilterType.UserLocale);
    });
  });

  describe('.removeFilter', () => {
    it('should remove filter', () => {
      const rule = component.featureFlags[0].rules[0];
      component.addNewFilter(rule);
      rule.filters[1].type = PlatformParameterFilterType.UserLocale;

      component.removeFilter(rule, 0);

      expect(rule.filters.length).toBe(1);
      expect(rule.filters[0].type)
        .toEqual(PlatformParameterFilterType.UserLocale);
    });
  });

  describe('.addNewCondition', () => {
    it('should add new condition', () => {
      const filter = component.featureFlags[0].rules[0].filters[0];

      component.addNewCondition(filter);
      filter.conditions[1] = ['=', 'mock'];

      expect(filter.conditions.length).toBe(2);
      expect(filter.conditions[0])
        .toEqual(['=', ServerMode.Dev.toString()]);
      expect(filter.conditions[1])
        .toEqual(['=', 'mock']);
    });
  });

  describe('.removeCondition', () => {
    it('should remove condition', () => {
      const filter = component.featureFlags[0].rules[0].filters[0];
      component.addNewCondition(filter);
      filter.conditions[1] = ['=', 'mock'];

      component.removeCondition(filter, 0);

      expect(filter.conditions.length).toBe(1);
      expect(filter.conditions[0]).toEqual(['=', 'mock']);
    });
  });

  describe('.clearFilterConditions', () => {
    it('should clear existing conditions', () => {
      const filter = component.featureFlags[0].rules[0].filters[0];
      component.addNewCondition(filter);
      filter.conditions[1] = ['=', 'mock'];

      component.clearFilterConditions(filter);
      expect(filter.conditions.length).toBe(0);
    });
  });

  describe('.clearChanges', () => {
    it('should clear changes', () => {
      const featureFlag = component.featureFlags[0];
      const originalRules = cloneDeep(featureFlag.rules);

      component.addNewRuleToTop(featureFlag);
      component.clearChanges(featureFlag);

      expect(featureFlag.rules.length).toBe(1);
      expect(featureFlag.rules).toEqual(originalRules);
    });

    it('should not proceed if the user doesn\'t confirm', () => {
      mockConfirmResult(false);
      const featureFlag = component.featureFlags[0];

      expect(featureFlag.rules.length).toBe(1);

      component.addNewRuleToTop(featureFlag);
      component.clearChanges(featureFlag);

      expect(featureFlag.rules.length).toBe(2);
    });
  });

  describe('.updateFeatureRulesAsync', () => {
    let setStatusSpy: jasmine.Spy;

    beforeEach(() => {
      setStatusSpy = jasmine.createSpy();
      setStatusSpy = spyOn(component.setStatusMessage, 'emit');

      adminTaskManagerService.finishTask();
    });

    it('should update feature rules', fakeAsync(() => {
      mockPromptResult('mock msg');

      const featureFlag = component.featureFlags[0];

      component.addNewRuleToTop(featureFlag);
      component.updateFeatureRulesAsync(featureFlag);

      flushMicrotasks();

      expect(updateApiSpy).toHaveBeenCalledWith(
        featureFlag.name, 'mock msg', featureFlag.rules);
      expect(setStatusSpy).toHaveBeenCalledWith('Saved successfully.');
    }));

    it('should update feature backup after update succeeds', fakeAsync(() => {
      mockPromptResult('mock msg');

      const featureFlag = component.featureFlags[0];

      component.addNewRuleToTop(featureFlag);
      component.updateFeatureRulesAsync(featureFlag);

      flushMicrotasks();

      expect(component.featureFlagNameToBackupMap.get(featureFlag.name))
        .toEqual(featureFlag);
    }));

    it('should not proceed if there is another task running', fakeAsync(() => {
      mockPromptResult('mock msg');

      adminTaskManagerService.startTask();

      const featureFlag = component.featureFlags[0];

      component.addNewRuleToTop(featureFlag);
      component.updateFeatureRulesAsync(featureFlag);

      flushMicrotasks();

      expect(updateApiSpy).not.toHaveBeenCalled();
      expect(setStatusSpy).not.toHaveBeenCalled();
    }));

    it('should not proceed if the user cancels the prompt', fakeAsync(
      () => {
        mockPromptResult(null);

        const featureFlag = component.featureFlags[0];

        component.addNewRuleToTop(featureFlag);
        component.updateFeatureRulesAsync(featureFlag);

        flushMicrotasks();

        expect(updateApiSpy).not.toHaveBeenCalled();
        expect(setStatusSpy).not.toHaveBeenCalled();
      })
    );

    it('should show error if the update fails', fakeAsync(() => {
      mockPromptResult('mock msg');

      updateApiSpy.and.rejectWith('unknown error');
      const featureFlag = component.featureFlags[0];

      component.addNewRuleToTop(featureFlag);
      component.updateFeatureRulesAsync(featureFlag);

      flushMicrotasks();

      expect(updateApiSpy).toHaveBeenCalled();
      expect(setStatusSpy).toHaveBeenCalledWith('Update failed.');
    }));

    it('should show error if the update fails', fakeAsync(() => {
      mockPromptResult('mock msg');

      updateApiSpy.and.rejectWith({
        error: {
          error: 'validation error.'
        }
      });
      const featureFlag = component.featureFlags[0];

      component.addNewRuleToTop(featureFlag);
      component.updateFeatureRulesAsync(featureFlag);

      flushMicrotasks();

      expect(updateApiSpy).toHaveBeenCalled();
      expect(setStatusSpy).toHaveBeenCalledWith(
        'Update failed: validation error.');
    }));
  });

  describe('server mode option filter', () => {
    let options: string[];
    let optionFilter: (feature: PlatformParameter, option: string) => boolean;

    beforeEach(() => {
      options = component
        .filterTypeToContext[PlatformParameterFilterType.ServerMode]
        .options;
      optionFilter = component
        .filterTypeToContext[PlatformParameterFilterType.ServerMode]
        .optionFilter;
    });

    it('should return [\'dev\'] for feature in dev stage', () => {
      expect(
        options.filter(option => optionFilter(
          <PlatformParameter>{featureStage: FeatureStage.DEV},
          option))
      )
        .toEqual(['dev']);
    });

    it('should return [\'dev\', \'test\'] for feature in test stage', () => {
      expect(
        options.filter(option => optionFilter(
          <PlatformParameter>{featureStage: FeatureStage.TEST},
          option))
      )
        .toEqual(['dev', 'test']);
    });

    it('should return [\'dev\', \'test\', \'prod\'] for feature in prod stage',
      () => {
        expect(
          options.filter(option => optionFilter(
            <PlatformParameter>{featureStage: FeatureStage.PROD},
            option))
        )
          .toEqual(['dev', 'test', 'prod']);
      }
    );

    it('should return empty array for feature in invalid stage', () => {
      expect(
        options.filter(option => optionFilter(
          <PlatformParameter>{featureStage: null},
          option))
      )
        .toEqual([]);
    });
  });
});

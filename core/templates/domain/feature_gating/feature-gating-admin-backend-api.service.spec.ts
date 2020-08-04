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
 * @fileoverview Unit tests for FeatureGatingAdminBackendApiService.
 */

import { HttpClientTestingModule, HttpTestingController } from
  '@angular/common/http/testing';
import { TestBed, fakeAsync, flushMicrotasks } from '@angular/core/testing';

import { FeatureGatingDomainConstants } from
  'domain/feature_gating/feature-gating-domain.constants';
import { FeatureGatingAdminBackendApiService } from
  'domain/feature_gating/feature-gating-admin-backend-api.service';
import { PlatformParameterRuleObjectFactory } from
  'domain/feature_gating/PlatformParameterRuleObjectFactory';

fdescribe('FeatureGatingAdminBackendApiService', () => {
  let featureAdminService: FeatureGatingAdminBackendApiService = null;
  let httpTestingController: HttpTestingController;
  let ruleFactory: PlatformParameterRuleObjectFactory = null;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule]
    });

    featureAdminService = TestBed.get(FeatureGatingAdminBackendApiService);
    httpTestingController = TestBed.get(HttpTestingController);
    ruleFactory = TestBed.get(PlatformParameterRuleObjectFactory);
  });

  afterEach(() => {
    httpTestingController.verify();
  });

  it('should make a reqeust to update the feature flag rules',
    fakeAsync(() => {
      const successHandler = jasmine.createSpy('success');
      const failHandler = jasmine.createSpy('fail');

      const newRules = [
        ruleFactory.createFromBackendDict({
          filters: [],
          value_when_matched: false
        })
      ];

      featureAdminService.updateFeatureFlag(
        'feature_name', 'update message', newRules
      ).then(successHandler, failHandler);

      const req = httpTestingController.expectOne(
        FeatureGatingDomainConstants.FEATURE_GATING_ADMIN_HANDLER_URL);
      req.flush({});
      expect(req.request.method).toEqual('POST');

      flushMicrotasks();

      expect(successHandler).toHaveBeenCalled();
      expect(failHandler).not.toHaveBeenCalled();
    })
  );
});

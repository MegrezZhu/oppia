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
 * @fileoverview Unit tests for PlatformParameterMetadataObjectFactory.
 */

import { TestBed } from '@angular/core/testing';

import {
  FeatureFlagStage,
  PlatformParameterMetadataObjectFactory,
} from 'domain/feature_gating/PlatformParameterMetadataObjectFactory';

describe('PlatformParameterMetadataObjectFactory', () => {
  let factory: PlatformParameterMetadataObjectFactory;

  beforeEach(() => {
    factory = TestBed.get(PlatformParameterMetadataObjectFactory);
  });

  it('should create an instance from a backend dict.', () => {
    const metadata = factory.createFromBackendDict({
      is_feature: true,
      feature_stage: FeatureFlagStage.DEV
    });

    expect(metadata.isFeature).toBeTrue();
    expect(metadata.featureStage).toEqual(FeatureFlagStage.DEV);
  });
});

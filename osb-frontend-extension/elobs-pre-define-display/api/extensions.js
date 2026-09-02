// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Katja Glass Consulting

import repository from '../../../api/repositoryExtensions'

export default {
  /**
   * List sponsor models (standards) with their extended CDISC IG (panel 3).
   * @returns {Promise<Array>}
   */
  async getStandards() {
    const { data } = await repository.get('/elobs-pre-define-display/standards')
    return data
  },

  /**
   * List datasets (domains) used by a study for a given standard/version (panel 4).
   * @param {string} uid          - StudyRoot uid
   * @param {string} sponsorModel - sponsor model name
   * @param {string} [version]    - study version; omit for latest
   * @returns {Promise<Array>}
   */
  async getDatasets(uid, sponsorModel, version = null) {
    const params = { sponsor_model: sponsorModel }
    if (version) params.version = version
    const { data } = await repository.get(
      `/elobs-pre-define-display/studies/${uid}/datasets`,
      { params },
    )
    return data
  },

  /**
   * List variables of a dataset as defined by the sponsor model (panel 5).
   * @param {string} dataset      - dataset/domain uid
   * @param {string} sponsorModel - sponsor model name
   * @returns {Promise<Array>}
   */
  async getVariables(dataset, sponsorModel) {
    const { data } = await repository.get(
      `/elobs-pre-define-display/datasets/${dataset}/variables`,
      { params: { sponsor_model: sponsorModel } },
    )
    return data
  },
}

import repository from '../../../api/repositoryExtensions'

export default {
  /**
   * Fetch the dummy greeting from the pre-define viewer extension.
   *
   * @returns {Promise<{ message: string }>} The greeting payload
   */
  async getHello() {
    const response = await repository.get('/elobs-pre-define-display/hello')
    return response.data
  },

  /**
   * Fetch study summaries (uid, study_id, acronym) from OpenStudyBuilder.
   *
   * @returns {Promise<Array<{ uid: string, study_id: string|null, acronym: string|null }>>}
   */
  async getStudies() {
    const response = await repository.get('/elobs-pre-define-display/studies')
    return response.data
  },
}

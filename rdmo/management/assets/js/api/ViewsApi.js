import isNil from 'lodash/isNil'

import BaseApi from 'rdmo/core/assets/js/api/BaseApi'

class ViewsApi extends BaseApi {

  static fetchViews(action) {
    let url = '/api/v1/views/views/'
    if (action == 'index') url += 'index/'
    return this.get(url)
  }

  static fetchView(id) {
    return this.get(`/api/v1/views/views/${id}/`)
  }

  static storeView(view, action) {
    if (isNil(view.id)) {
      return this.post('/api/v1/views/views/', view)
    } else {
      const actionPath = isNil(action) ? '' : `${action}/`
      return this.put(`/api/v1/views/views/${view.id}/${actionPath}`, view)
    }
  }

  static deleteView(view) {
    return this.delete(`/api/v1/views/views/${view.id}/`)
  }

}

export default ViewsApi

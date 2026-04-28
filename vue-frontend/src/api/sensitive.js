import request from '../utils/request'

export function detectText(data) {
  return request({
    url: '/detect',
    method: 'post',
    data
  })
}

export function getSensitiveWords(params) {
  return request({
    url: '/sensitive',
    method: 'get',
    params
  })
}

export function createSensitiveWord(data) {
  return request({
    url: '/sensitive',
    method: 'post',
    data
  })
}

export function updateSensitiveWord(id, data) {
  return request({
    url: `/sensitive/${id}`,
    method: 'put',
    data
  })
}

export function deleteSensitiveWord(id) {
  return request({
    url: `/sensitive/${id}`,
    method: 'delete'
  })
}

export function importSensitiveWords(data) {
  return request({
    url: '/sensitive/import',
    method: 'post',
    data
  })
}

export function downloadSensitiveTemplate() {
  return request({
    url: '/sensitive/template',
    method: 'get',
    responseType: 'blob'
  })
}
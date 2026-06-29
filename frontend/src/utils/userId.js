export function getUserId() {
  let uid = localStorage.getItem('datamind_user_id')
  if (!uid) {
    uid = crypto.randomUUID()
    localStorage.setItem('datamind_user_id', uid)
  }
  return uid
}

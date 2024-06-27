/* eslint-disable no-underscore-dangle */
class MainService {
  constructor() {
    const fileLocation = document.location.href.substr(0, document.location.href.lastIndexOf('/'));
    if (process.env.NODE_ENV === 'development') {
      this.baseUrl = `${window.location.protocol}//${window.location.hostname}:8000`;
    } else {
      this.baseUrl = `${fileLocation}`;
    }
  }

  async __deleteData(url) {
    return fetch(`${this.baseUrl}${url}`, {
      method: 'DELETE',
    });
  }

  async __fetchData(url) {
    const r = await fetch(`${this.baseUrl}${url}`);
    const data = await r.json();
    return data;
  }

  async __postData(url, data = {}) {
    const request = new Request(`${this.baseUrl}${url}`, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return fetch(request);
  }

  async __putData(url, data = {}) {
    const request = new Request(`${this.baseUrl}${url}`, {
      method: 'PUT',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return fetch(request);
  }

  async deleteProject(projectId) {
    await this.__deleteData(`/projects/${projectId}`);
  }

  async deleteGroup(groupId) {
    await this.__deleteData(`/groups/${groupId}`);
  }

  async deletePay(paymentId) {
    await this.__deleteData(`/payments/${paymentId}`);
  }

  async addProject(name) {
    await this.__postData('/projects', { name });
  }

  async addGroup(project, name) {
    await this.__postData('/groups', { project, name });
  }

  async addPayment(payment) {
    await this.__postData('/payments', payment);
  }

  async getProjects() {
    return this.__fetchData('/projects');
  }

  async getGroups(projectId) {
    return this.__fetchData(`/projects/${projectId}/groups`);
  }

  async getPayments(groupId) {
    return this.__fetchData(`/groups/${groupId}/payments`);
  }

  async updateProject(id, details) {
    await this.__putData(`/projects/${id}`, details);
  }

  async updateGroup(id, details) {
    await this.__putData(`/groups/${id}`, details);
  }

  async updatePayment(id, details) {
    await this.__putData(`/payments/${id}`, details);
  }
}

export default new MainService();

/* eslint-disable no-underscore-dangle */
class MainService {
  constructor() {
    const fileLocation = document.location.href.substring(0, document.location.href.lastIndexOf('/'));
    if (process.env.NODE_ENV === 'development') {
      this.baseUrl = `${window.location.protocol}//${window.location.hostname}:8000`;
    } else {
      this.baseUrl = `${fileLocation}`;
    }
    this.projectId = null;
    this.payGroupId = null;
    this.storedCurrencyPrecision = 100000000;
    this.__isReadOnly = false;
  }

  get isReadOnly() {
    return this.__isReadOnly;
  }

  async __deleteData(url) {
    if (this.isReadOnly) return;
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
    if (this.isReadOnly) return;
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
    if (this.isReadOnly) return;
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

  async deleteGroup(id) {
    await this.__deleteData(`/projects/${this.projectId}/paygroups/${id}`);
  }

  async deletePay(id) {
    await this.__deleteData(`/projects/${this.projectId}/paygroups/${this.payGroupId}/payments/${id}`);
  }

  async addProject(name) {
    await this.__postData('/projects', { name });
  }

  async addGroup(project, name) {
    await this.__postData(`/projects/${this.projectId}/paygroups`, { project, name });
  }

  async addPayment(payment) {
    await this.__postData(`/projects/${this.projectId}/paygroups/${this.payGroupId}/payments`, {
      ...payment,
      asset: Math.round(payment.paid * this.storedCurrencyPrecision),
      liability: Math.round(payment.owed * this.storedCurrencyPrecision),
    });
  }

  async getProjects() {
    return this.__fetchData('/projects');
  }

  setActiveGroup(groupId) {
    this.payGroupId = groupId;
  }

  async getProjectDetails(projectId, historyState = null) {
    let project;
    if (historyState) {
      project = await this.__fetchData(`/projects/${projectId}/history/${historyState}`);
      this.__isReadOnly = true;
    } else {
      project = await this.__fetchData(`/projects/${projectId}`);
      this.__isReadOnly = false;
    }
    project.paygroups.forEach((group) => {
      group.payments.forEach((pay) => {
        pay.paid = pay.asset / this.storedCurrencyPrecision;
        pay.owed = pay.liability / this.storedCurrencyPrecision;
      });
    });
    this.projectId = projectId;
    return project;
  }

  async updateProject(id, details) {
    await this.__putData(`/projects/${id}`, details);
  }

  async updateGroup(id, details) {
    await this.__putData(`/projects/${this.projectId}/paygroups/${id}`, details);
  }

  async updatePayment(id, payment) {
    await this.__putData(`/projects/${this.projectId}/paygroups/${this.payGroupId}/payments/${id}`, {
      ...payment,
      asset: Math.round(payment.paid * this.storedCurrencyPrecision),
      liability: Math.round(payment.owed * this.storedCurrencyPrecision),
    });
  }

  async uploadFile(id, file) {
    if (this.isReadOnly) return;
    const formData = new FormData();
    formData.append('file', file);
    await fetch(`${this.baseUrl}/projects/${this.projectId}/paygroups/${this.payGroupId}/payments/${id}/files`, {
      method: 'POST',
      body: formData,
    });
  }

  async getProjectHistory(projectId) {
    return this.__fetchData(`/projects/${projectId}/history`);
  }
}

export default new MainService();

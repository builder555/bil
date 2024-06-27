from datamodels import Project
import os
import json
class DBAdaptor:
    def __init__(self, path):
        self._base = path
        self._db_path = os.path.join(self._base, 'projects.json')

    def _get_project_path(self, project_id: int) -> str:
        return os.path.join(self._base, f'projects/{project_id}')

    def get_projects(self) -> list[Project]:
        projects = []
        if os.path.exists(self._db_path):
            with open(self._db_path, 'r') as f:
                projects = [Project(**p) for p in json.load(f)]
        return projects

    def _save_projects(self, projects: list[Project]):
        with open(self._db_path, 'w') as f:
            json.dump([p.model_dump() for p in projects], f)

    def _get_next_id(self, projects: list[Project]) -> int:
        if not projects:
            return 1
        return max([p.id for p in projects]) + 1

    def _mk_project_dir(self, project_id: int):
        project_path = self._get_project_path(project_id)
        os.makedirs(project_path)
        os.system(f'git init {project_path}')
    
    def _mk_project_db(self, project_id: int):
        project_path = self._get_project_path(project_id)
        os.system(f'touch {project_path}/payments.json')

    def add_project(self, name: str):
        projects = self.get_projects()
        new_id = self._get_next_id(projects)
        new_project = Project(name=name, id=new_id)
        self._mk_project_dir(new_id)
        self._mk_project_db(new_id)
        projects.append(new_project)
        self._save_projects(projects)

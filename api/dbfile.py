from datamodels import Paygroup, Project, ProjectEncoder, ProjectWithPayments
import os
import json

from functools import lru_cache


class DBAdaptor:
    def __init__(self, path):
        self._base = path
        self._db_path = os.path.join(self._base, "projects.json")

    def _get_project_path(self, project_id: int) -> str:
        return os.path.join(self._base, f"projects/{project_id}")

    @lru_cache
    def _get_projects_dict(self, include_deleted: bool = False) -> dict[int, Project]:
        projects = {}
        if os.path.exists(self._db_path):
            with open(self._db_path, "r") as f:
                projects = json.load(f)
                projects = {int(k): Project(**v) for k, v in projects.items() if not v["is_deleted"] or include_deleted}
        return projects

    @property
    def _projects_dict(self) -> dict[int, Project]:
        return self._get_projects_dict()

    @property
    def _all_projects_dict(self) -> dict[int, Project]:
        return self._get_projects_dict(include_deleted=True)

    def _get_payfile_path(self, project_id: int) -> str:
        return os.path.join(self._get_project_path(project_id), "payments.json")

    def _save_projects(self, projects: dict[int, Project]):
        with open(self._db_path, "w") as f:
            json.dump(projects, f, cls=ProjectEncoder, indent=4)
        self._get_projects_dict.cache_clear()

    def _get_next_id(self, items: dict[int, Project | Paygroup]) -> int:
        if not items:
            return 1
        return max(items.keys()) + 1

    def _mk_project_dir(self, project_id: int):
        project_path = self._get_project_path(project_id)
        os.makedirs(project_path)
        os.system(f"git init {project_path}")

    def get_projects(self, include_deleted: bool = False) -> list[Project]:
        if include_deleted:
            return list(self._all_projects_dict.values())
        return list(self._projects_dict.values())

    def add_project(self, name: str):
        projects = self._all_projects_dict
        new_id = self._get_next_id(projects)
        new_project = Project(name=name, id=new_id)
        self._mk_project_dir(new_id)
        projects[new_id] = new_project
        self._save_projects(projects)

    def delete_project(self, project_id: int):
        projects = self._projects_dict
        if project_id not in projects:
            raise ItemNotFoundError
        projects[project_id].is_deleted = True
        self._save_projects(projects)

    def get_project(self, project_id: int) -> ProjectWithPayments:
        projects = self._projects_dict
        if project_id not in projects:
            raise ItemNotFoundError
        project = ProjectWithPayments(**projects[project_id].model_dump(), paygroups={})
        groups = {}
        payfile_path = self._get_payfile_path(project_id)
        if os.path.exists(payfile_path):
            with open(payfile_path, "r") as f:
                groups = json.load(f)
        project.paygroups = {int(k): Paygroup(**v) for k, v in groups.items()}
        return project

    def _save_paygroups(self, project_id: int, paygroups: dict[int, Paygroup]):
        payfile_path = self._get_payfile_path(project_id)
        with open(payfile_path, "w") as f:
            json.dump(paygroups, f, cls=ProjectEncoder, indent=4)

    def add_paygroup(self, project_id: int, name: str):
        paygroups = self.get_paygroups(project_id)
        new_group_id = self._get_next_id(paygroups)
        new_paygroup = Paygroup(id=new_group_id, name=name)
        paygroups[new_group_id] = new_paygroup
        self._save_paygroups(project_id, paygroups)

    def get_paygroups(self, project_id: int) -> dict[int, Paygroup]:
        if project_id not in self._projects_dict:
            raise ItemNotFoundError
        groups = {}
        payfile_path = self._get_payfile_path(project_id)
        if os.path.exists(payfile_path):
            with open(self._get_project_path(project_id) + "/payments.json", "r") as f:
                groups = json.load(f)
        return {int(k): Paygroup(**v) for k, v in groups.items()}

    def delete_paygroup(self, project_id: int, paygroup_id: int):
        groups = self.get_paygroups(project_id)
        if paygroup_id not in groups:
            raise ItemNotFoundError
        del groups[paygroup_id]
        self._save_paygroups(project_id, groups)


class ItemNotFoundError(Exception):
    pass

from bil.datamodels import Payment, PaymentInput, Paygroup, Project, ProjectEncoder, ProjectWithPayments
import os
import shutil
import json
from typing import Mapping
from fastapi import UploadFile
import glob


class DBAdaptor:
    def __init__(self, path, keep_history=True):
        self.__keep_history = keep_history
        self._base = path
        self._db_path = os.path.join(self._base, "projects.json")

    def _get_project_path(self, project_id: int) -> str:
        return os.path.join(self._base, f"projects/{project_id}")

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

    def _get_next_id(self, items: Mapping[int, Project | Paygroup]) -> int:
        if not items:
            return 1
        return max(items.keys()) + 1

    def _mk_project_dir(self, project_id: int):
        project_path = self._get_project_path(project_id)
        os.makedirs(project_path)
        self.__repo_init(project_id)

    def __repo_init(self, project_id: int):
        if not self.__keep_history:
            return
        project_path = self._get_project_path(project_id)
        os.system(f"git -C {project_path} init")

    def __repo_commit(self, project_id: int):
        if not self.__keep_history:
            return
        project_path = self._get_project_path(project_id)
        os.system(f"git -C {project_path} add .")
        os.system(f"git -C {project_path} commit -m 'updated'")

    def __repo_checkout(self, project_id: int, commit_id: str):
        if not self.__keep_history:
            return
        project_path = self._get_project_path(project_id)
        os.system(f"git -C {project_path} checkout {commit_id}")

    def __repo_list(self, project_id: int) -> list[dict]:
        if not self.__keep_history:
            return []
        project_path = self._get_project_path(project_id)
        resp = os.popen(f'git -C {project_path} log --format="%h %ad"').read().splitlines()
        return [{"id": x.split(" ")[0], "date": x.split(" ")[1]} for x in resp]

    def _save_paygroups(self, project_id: int, paygroups: dict[int, Paygroup]):
        payfile_path = self._get_payfile_path(project_id)
        with open(payfile_path, "w") as f:
            json.dump(paygroups, f, cls=ProjectEncoder, indent=4)
        self.__repo_commit(project_id)

    def _get_paygroups_dict(self, project_id: int) -> dict[int, Paygroup]:
        if project_id not in self._projects_dict:
            raise ItemNotFoundError
        groups = {}
        payfile_path = self._get_payfile_path(project_id)
        if os.path.exists(payfile_path):
            with open(self._get_payfile_path(project_id), "r") as f:
                groups = json.load(f)
        return {int(k): Paygroup(**v) for k, v in groups.items()}

    def _get_paygroup(self, project_id: int, group_id: int) -> Paygroup:
        groups = self._get_paygroups_dict(project_id)
        if group_id not in groups:
            raise ItemNotFoundError
        return groups[group_id]

    def _get_payments_dict(self, project_id: int, group_id: int) -> dict[int, Payment]:
        paygroup = self._get_paygroup(project_id=project_id, group_id=group_id)
        return {p.id: p for p in paygroup.payments}

    def get_projects(self, include_deleted: bool = False) -> list[Project]:
        if include_deleted:
            return list(self._all_projects_dict.values())
        return list(self._projects_dict.values())

    def add_project(self, name: str) -> int:
        projects = self._all_projects_dict
        new_id = self._get_next_id(projects)
        new_project = Project(name=name, id=new_id)
        self._mk_project_dir(new_id)
        projects[new_id] = new_project
        self._save_projects(projects)
        return new_id

    def delete_project(self, project_id: int):
        projects = self._projects_dict
        if project_id not in projects:
            raise ItemNotFoundError
        projects[project_id].is_deleted = True
        self._save_projects(projects)

    def restore_project(self, project_id: int):
        projects = self._get_projects_dict(include_deleted=True)
        if project_id not in projects:
            raise ItemNotFoundError
        projects[project_id].is_deleted = False
        self._save_projects(projects)

    def get_project(self, project_id: int) -> ProjectWithPayments:
        def find_attachments(project_id: int, group_id: int, pay_id: int) -> bool:
            attachments = glob.glob(os.path.join(self._get_project_path(project_id), f"{group_id}_{pay_id}*"))
            file_name = ""
            if attachments:
                file_name = os.path.basename(attachments[0])
            return file_name

        projects = self._projects_dict
        if project_id not in projects:
            raise ItemNotFoundError
        project = ProjectWithPayments(**projects[project_id].model_dump(), paygroups=[])
        groups = {}
        payfile_path = self._get_payfile_path(project_id)
        if os.path.exists(payfile_path):
            with open(payfile_path, "r") as f:
                groups = json.load(f)
        for group in groups.values():
            for pay in group["payments"]:
                pay["attachment"] = find_attachments(project_id, group["id"], pay["id"])
        project.paygroups = [Paygroup(**v) for v in groups.values()]
        return project

    def update_project(self, project_id: int, name: str):
        projects = self._projects_dict
        if project_id not in projects:
            raise ItemNotFoundError
        projects[project_id].name = name
        self._save_projects(projects)

    def add_paygroup(self, project_id: int, name: str) -> int:
        paygroups = self._get_paygroups_dict(project_id)
        new_id = self._get_next_id(paygroups)
        new_paygroup = Paygroup(id=new_id, name=name)
        paygroups[new_id] = new_paygroup
        self._save_paygroups(project_id, paygroups)
        return new_id

    def get_paygroups(self, project_id: int) -> list[Paygroup]:
        return list(self._get_paygroups_dict(project_id).values())

    def delete_paygroup(self, project_id: int, paygroup_id: int):
        groups = self._get_paygroups_dict(project_id)
        if paygroup_id not in groups:
            raise ItemNotFoundError
        del groups[paygroup_id]
        self._save_paygroups(project_id, groups)

    def update_paygroup(self, project_id: int, paygroup_id: int, name: str):
        groups = self._get_paygroups_dict(project_id)
        if paygroup_id not in groups:
            raise ItemNotFoundError
        groups[paygroup_id].name = name
        self._save_paygroups(project_id, groups)

    def add_payment(self, project_id: int, paygroup_id: int, payment: PaymentInput) -> int:
        paygroup = self._get_paygroup(project_id, paygroup_id)
        payments = self._get_payments_dict(project_id, paygroup_id)
        new_id = self._get_next_id(payments)
        paygroup.payments.append(Payment(**payment.model_dump(), id=new_id))
        groups = {**self._get_paygroups_dict(project_id), paygroup_id: paygroup}
        self._save_paygroups(project_id, groups)
        return new_id

    def delete_payment(self, project_id: int, paygroup_id: int, pay_id: int):
        groups = self._get_paygroups_dict(project_id)
        payments = self._get_payments_dict(project_id, paygroup_id)
        if pay_id not in payments:
            raise ItemNotFoundError
        del payments[pay_id]
        groups[paygroup_id].payments = list(payments.values())
        self._save_paygroups(project_id, groups)

    def update_payment(self, project_id: int, paygroup_id: int, payment: Payment):
        groups = self._get_paygroups_dict(project_id)
        payments = self._get_payments_dict(project_id, paygroup_id)
        if payment.id not in payments:
            raise ItemNotFoundError
        payments[payment.id] = payment
        groups[paygroup_id].payments = list(payments.values())
        self._save_paygroups(project_id, groups)

    def add_file_to_payment(self, project_id: int, paygroup_id: int, payment_id: int, file: UploadFile):
        payments = self._get_payments_dict(project_id, paygroup_id)
        if payment_id not in payments:
            raise ItemNotFoundError
        project_folder = self._get_project_path(project_id)
        extension = os.path.splitext(file.filename)[1]
        file_name = os.path.join(project_folder, f"{paygroup_id}_{payment_id}{extension}")
        with open(file_name, "wb") as f:
            shutil.copyfileobj(file.file, f)
        self.__repo_commit(project_id)

    def get_files_from_payment(self, project_id: int, paygroup_id: int, payment_id: int) -> str:
        payments = self._get_payments_dict(project_id, paygroup_id)
        if payment_id not in payments:
            raise ItemNotFoundError
        project_folder = self._get_project_path(project_id)
        file_list = glob.glob(os.path.join(project_folder, f"{paygroup_id}_{payment_id}*"))
        if len(file_list) == 0:
            raise ItemNotFoundError
        return file_list[0]

    def delete_file_from_payment(self, project_id: int, paygroup_id: int, payment_id: int):
        payments = self._get_payments_dict(project_id, paygroup_id)
        if payment_id not in payments:
            raise ItemNotFoundError
        project_folder = self._get_project_path(project_id)
        file_list = glob.glob(os.path.join(project_folder, f"{paygroup_id}_{payment_id}*"))
        if len(file_list) == 0:
            raise ItemNotFoundError
        os.remove(file_list[0])
        self.__repo_commit(project_id)

    def get_project_history(self, project_id: int) -> list[dict]:
        return self.__repo_list(project_id)

    def get_project_state(self, project_id: int, history_id: str) -> ProjectWithPayments:
        self.__repo_checkout(project_id, history_id)
        project_state = self.get_project(project_id)
        self.__repo_checkout(project_id, "master")
        return project_state


class ItemNotFoundError(Exception):
    pass

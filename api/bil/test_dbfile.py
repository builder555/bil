import os
import shutil
from datamodels import Paygroup, PaygroupBase, Project
from dbfile import DBAdaptor, ItemNotFoundError
import pytest

DIR = "test_data"


@pytest.fixture
def db():
    yield DBAdaptor(DIR)
    if os.path.exists(DIR):
        shutil.rmtree(DIR)


def test_getting_projects_from_blank_db_returns_empty_list(db: DBAdaptor):
    assert db.get_projects() == []


def test_adding_new_project_creates_directory_with_git(db: DBAdaptor):
    db.add_project(name="test")
    assert os.path.exists(os.path.join(DIR, "projects", "1"))
    assert os.path.exists(os.path.join(DIR, "projects", "1", ".git"))


def test_can_get_all_projects(db: DBAdaptor):
    db.add_project(name="test1")
    db.add_project(name="test2")
    projects = db.get_projects()
    assert len(projects) == 2
    assert projects[0] == Project(name="test1", id=1)
    assert projects[1] == Project(name="test2", id=2)


def test_soft_deleting_project_removes_it_from_db(db: DBAdaptor):
    db.add_project(name="test")
    db.delete_project(1)
    assert not db.get_projects()


def test_soft_deleting_project_keeps_directory_intact(db: DBAdaptor):
    db.add_project(name="test")
    db.delete_project(1)
    assert os.path.exists(os.path.join(DIR, "projects", "1"))


def test_deleting_nonexistent_project_raises_error(db: DBAdaptor):
    with pytest.raises(ItemNotFoundError):
        db.delete_project(42)


def test_deleting_same_project_twice_raises_error(db: DBAdaptor):
    db.add_project(name="test")
    db.delete_project(1)
    with pytest.raises(ItemNotFoundError):
        db.delete_project(1)


def test_can_add_new_paygroup(db: DBAdaptor):
    db.add_project(name="test")
    db.add_paygroup(project_id=1, name="test paygroup")
    assert db.get_paygroups(project_id=1) == {1: Paygroup(id=1, name="test paygroup")}


def test_can_get_paygroups(db: DBAdaptor):
    db.add_project(name="test")
    db.add_paygroup(project_id=1, name="test paygroup")
    assert db.get_paygroups(project_id=1) == {1: Paygroup(id=1, name="test paygroup")}


def test_getting_paygroups_for_nonexistent_project_raises_error(db: DBAdaptor):
    with pytest.raises(ItemNotFoundError):
        db.get_paygroups(project_id=1)


def test_deleting_nonexistent_paygroup_raises_error(db: DBAdaptor):
    db.add_project(name="test")
    with pytest.raises(ItemNotFoundError):
        db.delete_paygroup(project_id=1, paygroup_id=42)


def test_can_delete_paygroup(db: DBAdaptor):
    db.add_project(name="test")
    db.add_paygroup(project_id=1, name="test paygroup")
    db.delete_paygroup(project_id=1, paygroup_id=1)
    assert not db.get_paygroups(project_id=1)


def test_can_view_previous_states_of_project(db: DBAdaptor):
    pass

import os
import shutil
from datamodels import Project
from dbfile import DBAdaptor, ItemNotFoundError
import pytest
DIR = "test_data"
@pytest.fixture
def db():
    yield DBAdaptor(DIR)
    if os.path.exists(DIR):
        shutil.rmtree(DIR)

def test_getting_projects_from_blank_db_returns_empty_dict(db: DBAdaptor):
    assert db.get_projects() == {}

def test_adding_new_project_creates_directory_with_git(db: DBAdaptor):
    db.add_project(name="test")
    assert os.path.exists(os.path.join(DIR, "projects", "1"))
    assert os.path.exists(os.path.join(DIR, "projects", "1", ".git"))

def test_can_get_all_projects(db: DBAdaptor):
    db.add_project(name="test1")
    db.add_project(name="test2")
    projects = list(db.get_projects().values())
    assert len(projects) == 2
    assert projects[0] == Project(name="test1", id=1)
    assert projects[1] == Project(name="test2", id=2)

def test_soft_deleting_project_keeps_directory_intact(db: DBAdaptor):
    db.add_project(name="test")
    db.delete_project(1)
    assert not db.get_projects()
    assert os.path.exists(os.path.join(DIR, "projects", "1"))

def test_deleting_nonexistent_project_raises_error(db: DBAdaptor):
    with pytest.raises(ItemNotFoundError):
        db.delete_project(42)

def test_deleting_same_project_twice_raises_error(db: DBAdaptor):
    db.add_project(name="test")
    db.delete_project(1)
    with pytest.raises(ItemNotFoundError):
        db.delete_project(1)


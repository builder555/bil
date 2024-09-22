import os
import shutil
from bil.datamodels import PaymentInput, Paygroup, Project
from bil.dbfile import DBAdaptor, ItemNotFoundError
import pytest

DIR = "test_data"


@pytest.fixture
def db(fs):
    yield DBAdaptor(DIR)
    if os.path.exists(DIR):
        shutil.rmtree(DIR)


def test_getting_projects_from_blank_db_returns_empty_list(db: DBAdaptor):
    assert db.get_projects() == []


def test_adding_new_project_creates_directory_with_git(db: DBAdaptor):
    new_id = db.add_project(name="test")
    assert os.path.exists(os.path.join(DIR, "projects", f"{new_id}"))
    assert os.path.exists(os.path.join(DIR, "projects", f"{new_id}", ".git"))


def test_can_get_all_projects(db: DBAdaptor):
    id1 = db.add_project(name="test1")
    id2 = db.add_project(name="test2")
    projects = db.get_projects()
    assert len(projects) == 2
    assert projects[0] == Project(name="test1", id=id1)
    assert projects[1] == Project(name="test2", id=id2)


def test_soft_deleting_project_removes_it_from_db(db: DBAdaptor):
    new_id = db.add_project(name="test")
    db.delete_project(new_id)
    assert not db.get_projects()


def test_soft_deleting_project_keeps_directory_intact(db: DBAdaptor):
    new_id = db.add_project(name="test")
    db.delete_project(new_id)
    assert os.path.exists(os.path.join(DIR, "projects", f"{new_id}"))


def test_deleting_nonexistent_project_raises_error(db: DBAdaptor):
    with pytest.raises(ItemNotFoundError):
        db.delete_project(42)


def test_deleting_same_project_twice_raises_error(db: DBAdaptor):
    new_id = db.add_project(name="test")
    db.delete_project(new_id)
    with pytest.raises(ItemNotFoundError):
        db.delete_project(new_id)


def test_can_add_new_paygroup(db: DBAdaptor):
    project_id = db.add_project(name="test")
    assert len(db.get_paygroups(project_id=project_id)) == 0
    db.add_paygroup(project_id=project_id, name="test paygroup")
    assert len(db.get_paygroups(project_id=project_id)) == 1


def test_can_get_paygroups(db: DBAdaptor):
    project_id = db.add_project(name="test")
    group_id = db.add_paygroup(project_id=project_id, name="test paygroup")
    assert db.get_paygroups(project_id=project_id) == [Paygroup(id=group_id, name="test paygroup")]


def test_getting_paygroups_for_nonexistent_project_raises_error(db: DBAdaptor):
    with pytest.raises(ItemNotFoundError):
        db.get_paygroups(project_id=42)


def test_deleting_nonexistent_paygroup_raises_error(db: DBAdaptor):
    project_id = db.add_project(name="test")
    with pytest.raises(ItemNotFoundError):
        db.delete_paygroup(project_id=project_id, paygroup_id=42)


def test_can_delete_paygroup(db: DBAdaptor):
    project_id = db.add_project(name="test")
    group_id = db.add_paygroup(project_id=project_id, name="test paygroup")
    db.delete_paygroup(project_id=project_id, paygroup_id=group_id)
    assert len(db.get_paygroups(project_id=project_id)) == 0


def test_cannot_add_payment_without_asset_or_liability(db: DBAdaptor):
    project_id = db.add_project(name="test")
    group_id = db.add_paygroup(project_id=project_id, name="test paygroup")
    with pytest.raises(ValueError):
        payment = PaymentInput(name="test payment", date="2022-01-01")
        db.add_payment(project_id=project_id, paygroup_id=group_id, payment=payment)


def test_can_add_payment_with_asset_only(db: DBAdaptor):
    project_id = db.add_project(name="test")
    group_id = db.add_paygroup(project_id=project_id, name="test paygroup")
    payment = PaymentInput(name="test payment", date="2022-01-01", asset=10000)
    db.add_payment(project_id=project_id, paygroup_id=group_id, payment=payment)
    # assert db.get_payments(project_id=1) == {1: [payment]}


def test_can_add_payment_with_liability_only(db: DBAdaptor):
    project_id = db.add_project(name="test")
    group_id = db.add_paygroup(project_id=project_id, name="test paygroup")
    payment = PaymentInput(name="test payment", date="2022-01-01", liability=100)
    db.add_payment(project_id=project_id, paygroup_id=group_id, payment=payment)


@pytest.mark.skip
def test_can_view_previous_states_of_project(db: DBAdaptor):
    # WHEN THIS IS IMPLEMENTED, REMOVE THE TEST CHECKING FOR .git IN THE PROJECTS DIRECTORY
    pass

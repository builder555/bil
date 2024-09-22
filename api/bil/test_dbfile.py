import os
import random
import shutil
from bil.datamodels import Payment, PaymentInput, Paygroup, Project
from bil.dbfile import DBAdaptor, ItemNotFoundError
import pytest

DIR = "test_data"


@pytest.fixture
def db(fs):
    yield DBAdaptor(DIR)
    if os.path.exists(DIR):
        shutil.rmtree(DIR)


@pytest.fixture
def db_with_group(db: DBAdaptor) -> tuple[DBAdaptor, int, int]:
    project_id = db.add_project(name="test")
    group_id = db.add_paygroup(project_id=project_id, name="test paygroup")
    return (db, project_id, group_id)


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


def test_can_delete_paygroup(db_with_group: tuple[DBAdaptor, int, int]):
    db, project_id, group_id = db_with_group
    db.delete_paygroup(project_id=project_id, paygroup_id=group_id)
    assert len(db.get_paygroups(project_id=project_id)) == 0


def test_cannot_add_payment_without_asset_or_liability(db_with_group: tuple[DBAdaptor, int, int]):
    db, project_id, group_id = db_with_group
    with pytest.raises(ValueError):
        db.add_payment(
            project_id=project_id,
            paygroup_id=group_id,
            payment=PaymentInput(name="test payment", date="2022-01-01"),
        )


def test_cannot_add_payment_to_nonexistent_paygroup(db_with_group: tuple[DBAdaptor, int, int]):
    db, project_id, _ = db_with_group
    with pytest.raises(ItemNotFoundError):
        db.add_payment(
            project_id=project_id,
            paygroup_id=42,
            payment=PaymentInput(name="test payment", date="2022-01-01", asset=100),
        )


def test_can_add_payment_with_asset_only(db_with_group: tuple[DBAdaptor, int, int]):
    db, project_id, group_id = db_with_group
    payment = PaymentInput(name="test payment", date="2022-01-01", asset=10000)
    db.add_payment(project_id=project_id, paygroup_id=group_id, payment=payment)


def test_can_add_payment_with_liability_only(db_with_group: tuple[DBAdaptor, int, int]):
    db, project_id, group_id = db_with_group
    payment = PaymentInput(name="test payment", date="2022-01-01", liability=10000)
    db.add_payment(project_id=project_id, paygroup_id=group_id, payment=payment)


def test_added_payments_are_stored_in_paygroups(db_with_group: tuple[DBAdaptor, int, int]):
    db, project_id, group_id = db_with_group
    payment = PaymentInput(name="test payment", date="2022-01-01", liability=10000, asset=20000)
    db.add_payment(project_id=project_id, paygroup_id=group_id, payment=payment)
    paygroup = db.get_paygroups(project_id=project_id)[0]
    assert len(paygroup.payments) == 1
    assert paygroup.payments[0].liability == payment.liability
    assert paygroup.payments[0].asset == payment.asset
    assert paygroup.payments[0].date == payment.date
    assert paygroup.payments[0].name == payment.name


def test_cannot_delete_nonexistent_payment(db_with_group: tuple[DBAdaptor, int, int]):
    db, project_id, group_id = db_with_group
    with pytest.raises(ItemNotFoundError):
        db.delete_payment(project_id=project_id, paygroup_id=group_id, pay_id=42)


def test_can_delete_payment(db_with_group: tuple[DBAdaptor, int, int]):
    db, project_id, group_id = db_with_group
    payment = PaymentInput(name="test payment", date="2022-01-02", liability=10000)
    pay1 = db.add_payment(project_id=project_id, paygroup_id=group_id, payment=payment)
    pay2 = db.add_payment(project_id=project_id, paygroup_id=group_id, payment=payment)
    db.delete_payment(project_id=project_id, paygroup_id=group_id, pay_id=pay1)
    paygroup = db.get_paygroups(project_id=project_id)[0]
    assert len(paygroup.payments) == 1
    assert paygroup.payments[0].id == pay2


def test_can_update_payment(db_with_group: tuple[DBAdaptor, int, int]):
    db, project_id, group_id = db_with_group
    initial_payment = PaymentInput(name="test payment", date="2022-01-02", liability=10000)
    pay1 = db.add_payment(project_id=project_id, paygroup_id=group_id, payment=initial_payment)
    updated_payment = Payment(id=pay1, name="test payment updated", date="2022-01-03", liability=20000, asset=30000)
    db.update_payment(project_id=project_id, paygroup_id=group_id, payment=updated_payment)
    paygroup = db.get_paygroups(project_id=project_id)[0]
    stored_payment = paygroup.payments[0]
    assert stored_payment.name == updated_payment.name
    assert stored_payment.date == updated_payment.date
    assert stored_payment.liability == updated_payment.liability
    assert stored_payment.asset == updated_payment.asset


def test_can_update_paygroup_name(db_with_group: tuple[DBAdaptor, int, int]):
    db, project_id, group_id = db_with_group
    random_number = random.randint(0, 1000)
    new_name = f"new paygroup name {random_number}"
    db.update_paygroup(project_id=project_id, paygroup_id=group_id, name=new_name)
    paygroup = db.get_paygroups(project_id=project_id)[0]
    assert paygroup.name == new_name


@pytest.mark.skip
def test_can_update_project_name(db_with_group: tuple[DBAdaptor, int, int]):
    pass


@pytest.mark.skip
def test_can_add_files_to_payment(db_with_group: tuple[DBAdaptor, int, int]):
    pass


@pytest.mark.skip
def test_can_remove_files_from_payment(db_with_group: tuple[DBAdaptor, int, int]):
    pass


@pytest.mark.skip
def test_can_view_previous_states_of_project(db: DBAdaptor):
    # WHEN THIS IS IMPLEMENTED, REMOVE THE TEST CHECKING FOR .git IN THE PROJECTS DIRECTORY
    pass

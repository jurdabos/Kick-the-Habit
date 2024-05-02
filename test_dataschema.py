from test_project import setup_test_database
from freezegun import freeze_time
from datetime import date
import pytest
import dataschema

fake_today = "2024-04-23"


@freeze_time(fake_today)
def test_current_date():
    assert date.today() == date.fromisoformat(fake_today)


class TestDB:
    def __init__(self):
        self.test_db = None

    def setup_method(self):
        self.test_db = setup_test_database()

    def teardown_method(self):
        dataschema.clear_database(self.test_db)

    def test_add_habit_to_db(self):
        # Testing adding a new habit to the database
        dataschema.add_habit_to_db(self.test_db,
                                   name='Running too quickly',
                                   descr='Run with a speed more than comfortable',
                                   gen_date=date.today(),
                                   periodicity='Daily')
        habit_data = dataschema.get_habit_data(self.test_db, 'Running too quickly')
        assert habit_data is not None
        assert len(habit_data) == 1
        assert habit_data[0]['name'] == 'Running too quickly'
        assert habit_data[0]['descr'] == 'Run with a speed more than comfortable'
        assert habit_data[0]['periodicity'] == 'Daily'

    def test_increment_guilt(self):
        # Testing incrementing guilt for a habit
        dataschema.add_habit_to_db(self.test_db,
                                   name='Smoking in the pool',
                                   descr='Lighting a cigar while doing the butterfly',
                                   gen_date=date.today(),
                                   periodicity='Weekly')
        dataschema.increment_guilt(self.test_db, name='Smoking in the pool')
        habit_data = dataschema.get_habit_data(self.test_db, 'Smoking in the pool')
        assert habit_data is not None
        assert len(habit_data) == 1
        assert habit_data[0]['name'] == 'Smoking in the pool'
        assert 'check_off_dates' in habit_data[0]
        assert len(habit_data[0]['check_off_dates']) == 1


if __name__ == "__main__":
    pytest.main()

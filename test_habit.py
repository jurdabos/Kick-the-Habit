from test_project import setup_test_database
from datetime import date
from freezegun import freeze_time
import pytest
import dataschema
import pandas as pd
from habit import Habit

fake_today = "2024-04-23"


@freeze_time(fake_today)
def test_current_date():
    assert date.today() == date.fromisoformat(fake_today)


class TestHabit:
    def __init__(self):
        self.test_db = None

    def setup_method(self):
        self.test_db = setup_test_database()

    def teardown_method(self):
        dataschema.clear_database(self.test_db)

    def test_habit_creation(self):
        habits_data = pd.read_sql_query("SELECT * FROM habit", self.test_db)
        for index, row in habits_data.iterrows():
            Habit.create_habit(row['name'], row['descr'], row['gen_date'], row['periodicity'], db=self.test_db)
        assert Habit("Procrastipondering") is not None
        assert Habit("Rushing") is not None

    def test_streak_computation(self):
        stats_table = Habit("Binge Watching").get_individual_stats()
        assert stats_table is not None
        assert stats_table['Current streak'][0] == 1
        assert stats_table['Longest streak'][0] == 1
        assert stats_table['Average streak'][0] == 1.0


if __name__ == "__main__":
    pytest.main()

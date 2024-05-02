from test_project import setup_test_database
from freezegun import freeze_time
from datetime import date
import pytest
import dataschema
import pandas as pd
import dataframe

fake_today = "2024-04-23"


@freeze_time(fake_today)
def test_current_date():
    assert date.today() == date.fromisoformat(fake_today)


class TestDataframe:
    def setup_method(self):
        self.test_db = setup_test_database()

    def teardown_method(self):
        dataschema.clear_database(self.test_db)

    # Test cases for the function display_all_habits_tracked
    def test_display_all_habits_tracked(self):
        df = dataframe.display_all_habits_tracked(self.test_db)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        # 5 test habits are added in setup_test_database
        assert len(df) == 5

    # Test cases for the function display_all_same_periodicity_habits_tracked
    def test_display_all_same_periodicity_habits_tracked(self):
        df = dataframe.display_all_same_periodicity_habits_tracked(self.test_db, periodicity='Daily')
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        # 2 daily test habits are added in setup_test_database
        assert len(df) == 2
        df2 = dataframe.display_all_same_periodicity_habits_tracked(self.test_db, periodicity='Weekly')
        assert isinstance(df2, pd.DataFrame)
        assert not df2.empty
        # 2 weekly test habits are added in setup_test_database
        assert len(df2) == 2
        df3 = dataframe.display_all_same_periodicity_habits_tracked(self.test_db, periodicity='Monthly')
        assert isinstance(df3, pd.DataFrame)
        assert not df3.empty
        # 1 monthly test habits are added in setup_test_database
        assert len(df3) == 1

    def test_calculate_longestrun_current_streak(self):
        df = dataframe.calculate_longestrun_current_streak(self.test_db)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        # Ensuring the DataFrame has the expected columns
        assert 'Name' in df.columns
        assert 'Current streak' in df.columns
        # Asserting that the longest-run current streak is for 'Overanalyzing'
        assert (df['Name'] == 'Overanalyzing').any(), "Longest streak is not for habit 'Overanalyzing'"

    def test_calculate_longest_historical_streak(self):
        df = dataframe.calculate_longest_historical_streak(self.test_db)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        # Ensuring the DataFrame has the columns with the relevant names
        assert 'Name' in df.columns
        assert 'Longest historical streak' in df.columns
        # Asserting that the longest-run historical streak is for 'Procrastipondering'
        assert (df['Name'] == 'Procrastipondering').any()

    def test_calculate_lowest_and_largest_average_streak(self):
        df = dataframe.calculate_lowest_and_largest_average_streak(self.test_db)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        # Ensuring the DataFrame has the expected columns
        assert 'Name' in df.columns
        assert 'Average streak' in df.columns
        assert 'Label' in df.columns
        # Asserting that the labels are correct
        assert df['Label'].isin(['Lowest', 'Largest']).all()
        # Checking if Binge watching has the lowest average streak with a value of 1
        binge_watching_row = df[df['Name'] == 'Binge watching']
        assert not binge_watching_row.empty
        assert binge_watching_row['Average streak'].iloc[0] == 1

    def test_calculate_lowest_and_highest_resistance_ratio(self):
        df = dataframe.calculate_lowest_and_highest_resistance_ratio(self.test_db)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        # Ensuring the Dataframe has the columns it should have
        assert 'Name' in df.columns
        assert 'Resistance ratio' in df.columns
        # Asserting that Procrastipondering has the lowest resistance ratio
        min_resistance_row = df[df['Name'] == 'Procrastipondering']
        assert not min_resistance_row.empty
        assert min_resistance_row['Resistance ratio'].iloc[0] == min(df['Resistance ratio'])


if __name__ == "__main__":
    pytest.main()

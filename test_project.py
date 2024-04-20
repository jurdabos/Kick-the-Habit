# import os
# import pytest
# from dataschema import get_db, add_habit, increment_streak
# from habit import Habit
# import pandas as pd
# from datetime import datetime
#
#
# @pytest.fixture
# def habit():
#     return Habit("Test_Habit", "Test_Description")
#
#
# class TestHabit:
#     def setup_method(self):
#         self.db = get_db("test.db")
#         add_habit(self.db, "Test_Habit", "Test_Description")
#         increment_streak(self.db, "Test_Habit", "2001-11-11")
#         increment_streak(self.db, "Test_Habit", "2001-11-12")
#         increment_streak(self.db, "Test_Habit", "2011-11-11")
#         increment_streak(self.db, "Test_Habit", "2021-11-11")
#
#     def test_habit(self, habit):
#         habit.store(self.db)
#
#         habit.mark_complete()
#         habit.add_event(self.db)
#         habit.calc_individual_stats()
#
#     def teardown_method(self):
#         self.db.close()
#         os.remove("test.db")

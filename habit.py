import shutil

import pandas as pd
from datetime import timedelta, date, datetime
from dataschema import add_habit_to_db, increment_guilt
from tabulate import tabulate
import math
from dateutil.relativedelta import relativedelta
from abc import ABC, abstractmethod
import json
from typing import Union


class Habit:
    def __init__(
            self,
            name="",
            descr="",
            gen_date: Union[str, date] = date.today(),
            periodicity="Daily",
            check_off_dates=None
    ):
        """
        Habit class constructor designed to create habit objects.
        :param name: the name of the habit
        :param descr: the description of the habit
        :param gen_date: the date when the habit was created
        :param periodicity: one of three values: daily, weekly, monthly
        """
        self.name = name
        self.descr = descr
        # Checking if gen_date is already a datetime.date object
        if isinstance(gen_date, date):
            self.gen_date = gen_date
        else:
            # Converting a potential string to a datetime.date data type object
            self.gen_date = datetime.strptime(gen_date, '%Y-%m-%d').date()
        self.periodicity = periodicity
        self.marked_complete = check_off_dates if check_off_dates else []

    @classmethod
    def create_habit(cls, name="", descr="", gen_date=date.today(), periodicity="Daily", db=None):
        """
        Class method to create instances of Habit and its subclasses based on periodicity.
        :param name: the name of the habit
        :param descr: the description of the habit
        :param gen_date: the date when the habit was created or the start date of data tracking
        :param periodicity: one of three string values: daily, weekly, monthly
        :param db: the database connection object
        :return: an instance of Habit or one of its subclasses
        """
        if periodicity == "Daily":
            habit = DailyHabit(name, descr, gen_date)
        elif periodicity == "Weekly":
            habit = WeeklyHabit(name, descr, gen_date)
        elif periodicity == "Monthly":
            habit = MonthlyHabit(name, descr, gen_date)
        else:
            # To default to creating a generic Habit instance for unknown periodicities
            habit = cls(name, descr, gen_date, periodicity)
        # If database connection is provided, retrieve check-off dates from the database.
        if db:
            habit.marked_complete = cls.get_check_off_dates_from_db(db, name)
        return habit

    @staticmethod
    def get_check_off_dates_from_db(db, name):
        """
        Retrieves and sorts check-off dates from the database for a specific habit.
        :param db: the database connection object
        :param name: the name of the habit
        :return: a sorted list of check-off dates
        """
        cur = db.cursor()
        try:
            cur.execute("SELECT check_off_dates FROM habit WHERE name=?", (name,))
            result = cur.fetchone()
            if result:
                check_off_dates_str = result[0]
                check_off_dates = json.loads(check_off_dates_str) if check_off_dates_str else []
                sorted_check_off_dates = sorted(check_off_dates)
                return [datetime.strptime(date_str, "%Y-%m-%d").date() for date_str in sorted_check_off_dates]
            else:
                return []
        except Exception as e:
            print(f"Error retrieving check-off dates for habit {name} from the database: {e}")
            return []
        finally:
            cur.close()

    @abstractmethod
    def mark_complete(self, db, mark_date=None):
        """
        Default implementation for the mark_complete method, so it can be used in the subclasses
        :return 0 as a default value
        """
        return 0

    def calc_individual_stats(self):
        """
        Calculates individual statistics for each habit it is run on.
        :return: a Pandas DataFrame containing info on current guilty streak, total completed, total resisted, ratio,
                 longest historical streak, and average streak length
        """
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        # Calling the methods from the subclasses to calculate statistics
        current_streak = self.calculate_current_streak()
        total_completed = self.calculate_total_completed()
        total_resisted = self.calculate_total_resisted()
        resistance_ratio = self.calculate_resistance_ratio()
        longest_streak = self.calculate_longest_historical_streak()
        average_streak = self.calculate_average_streak_length()

        # Returning the DataFrame directly
        return pd.DataFrame({
            'Name': [self.name],
            'Recording from': [self.gen_date.strftime("%Y/%m/%d")],
            'Periodicity': [self.periodicity],
            'Current streak': [current_streak],
            'Total periods of guilt': [total_completed],
            'Total periods of innocence': [total_resisted],
            'Resistance ratio': [resistance_ratio],
            'Longest streak': [longest_streak],
            'Average streak': [average_streak]
        })

    @abstractmethod
    def calculate_current_streak(self):
        """
        Default implementation for the current streak calculation.
        :return: 0 as a default value
        """
        return 0

    def calculate_total_completed(self):
        """
        Calculates the total number of periods the habit was completed on.
        It is a function of the Habit class, because it is calculated the same way regardless of periodicity.
        :return: the value of the total number of guilty periods as an integer
        """
        # Converting to set for the calculation to ensure each period is only counted once
        total_completed = len(set(self.marked_complete))
        total_completed = int(total_completed)
        return total_completed

    @abstractmethod
    def calculate_total_resisted(self):
        """
        Default implementation for total resisted calculation.
        :return: 0 as a default value
        """
        return 0

    @abstractmethod
    def calculate_resistance_ratio(self):
        """
        Default implementation for resistance ratio calculation.
        :return: "0%" as a default value
        """
        return "0%"

    @abstractmethod
    def calculate_longest_historical_streak(self):
        """
        Default implementation for the longest historical streak calculation.
        :return: 0 as a default value
        """
        return 0

    @abstractmethod
    def calculate_average_streak_length(self):
        """
        Default implementation for average streak length calculation.
        :return: 0.0 as a default value
        """
        return 0.0

    def get_individual_stats(self):
        """
        Takes the dataframe from the calc_individual_stats function and displays it as a table
        with barriers between the rows and columns, dynamic column widths and handling for screen size.
        :return: reformatted pandas dataframe
        """
        stats = self.calc_individual_stats()
        # Getting the terminal width to adjust column widths dynamically
        terminal_width = shutil.get_terminal_size().columns
        # Modifying column headers to include line breaks after each word
        modified_headers = [header.replace(" ", "\n") for header in stats.columns]

        # Tabulating the DataFrame for pretty printing
        formatted_table = tabulate(
            stats,
            headers=modified_headers,
            tablefmt='pretty',
            showindex=False,
            colalign=("center",) * len(stats.columns),
            numalign='center',
            maxcolwidths=[int(terminal_width / len(stats.columns))] * len(stats.columns)
        )
        return formatted_table

    def store(self, db_conn_obj_habit_store):
        """
        Stores the habit in the database.
        :param db_conn_obj_habit_store: the database connection
        """
        # Calling the add_habit_to_db function to add the habit to the database
        add_habit_to_db(db_conn_obj_habit_store, self.name, self.descr, self.gen_date, self.periodicity)

    def add_event(self, db_conn_obj_habit_ae, event_date: date = None):
        """
        Adds an event for the habit in the database, incrementing the guilt.
        :param db_conn_obj_habit_ae: the database connection
        :param event_date: the date of the event (default is today)
        """
        # Converting event_date to string if it's not None to conform with database standards
        event_date_str = event_date.strftime('%Y-%m-%d') if event_date else None
        increment_guilt(db_conn_obj_habit_ae, self.name, event_date_str)
        # Updating gen_date in the database in case it is necessary after new check-off
        self.update_gen_date(db_conn_obj_habit_ae, self.gen_date)

    def update_gen_date(self, db_conn_obj_habit_ugd, new_gen_date):
        """
        Updates the gen_date of the habit in the database.
        :param db_conn_obj_habit_ugd: the database connection
        :param new_gen_date: the updated gen_date for the habit
        """
        cur = db_conn_obj_habit_ugd.cursor()
        try:
            # Converting new_gen_date to the appropriate string format for the database
            new_gen_date_str = new_gen_date.strftime('%Y-%m-%d')
            # Executing an SQL update query to update the gen_date for the habit in the database
            cur.execute("UPDATE habit SET gen_date=? WHERE name=?", (new_gen_date_str, self.name))
            db_conn_obj_habit_ugd.commit()
            # print(f"Successfully updated gen_date for habit {self.name} in the database.")
        except Exception as e:
            print(f"Error updating gen_date for habit {self.name}: {e}")
        finally:
            cur.close()

    @staticmethod
    def get_habit_by_name(db_conn_obj_habit_ghbn, name):
        """
        Recreates a Habit object from the database based on the stored data.
        :param db_conn_obj_habit_ghbn: An SQLite database connection object
        :param name: Name of the habit in question
        :return: Habit object or None if not found
        """
        cur = db_conn_obj_habit_ghbn.cursor()
        try:
            cur.execute("SELECT name, descr, gen_date, periodicity, check_off_dates FROM habit WHERE name=?", (name,))
            result = cur.fetchone()
            if result:
                # Excluding the last element, the JSON-serialized check-off dates
                core_habit_data = result[:-1]
                # Extracting the check-off dates
                check_off_dates_str = result[-1]
                check_off_dates = json.loads(check_off_dates_str) if check_off_dates_str else []
                # Converting check-off dates from strings to date objects
                check_off_dates = [datetime.strptime(date_str, "%Y-%m-%d").date() for date_str in check_off_dates]
                # Sorting the check-off dates
                sorted_check_off_dates = sorted(check_off_dates)
                # Extracting periodicity from database result
                periodicity = result[3]
                # Instantiate the appropriate subclass based on periodicity
                if periodicity == "Daily":
                    habit_data_without_periodicity = core_habit_data[:-1]
                    recreated_habit = DailyHabit(*habit_data_without_periodicity)
                elif periodicity == "Weekly":
                    habit_data_without_periodicity = core_habit_data[:-1]
                    recreated_habit = WeeklyHabit(*habit_data_without_periodicity)
                elif periodicity == "Monthly":
                    habit_data_without_periodicity = core_habit_data[:-1]
                    recreated_habit = MonthlyHabit(*habit_data_without_periodicity)
                else:
                    # Default to generic Habit if periodicity is unknown
                    recreated_habit = Habit(*core_habit_data)
                # Assigning check-off dates to marked_complete list
                recreated_habit.marked_complete = sorted_check_off_dates
                return recreated_habit
            else:
                return None
        except Exception as e:
            # Logging the exception
            print(f"Error retrieving Habit by name: {e}")
            return None
        finally:
            cur.close()


class DailyHabit(Habit):
    def __init__(self, name="", descr="", gen_date=date.today()):
        super().__init__(name, descr, gen_date, periodicity="Daily")

    def mark_complete(self, db, mark_date=None):
        """
        Marks the habit as complete on a specific date.
        :param db: The database connection where the marking of the habit will be stores
        :param mark_date: the date on which to mark the habit as complete
        """
        if mark_date is None:
            mark_date = date.today()
        self.marked_complete.append(mark_date)
        if mark_date != date.today() and mark_date < self.gen_date:
            self.gen_date = mark_date
        self.update_gen_date(db, self.gen_date)
        self.marked_complete.sort()

    def calculate_current_streak(self):
        """
        Calculates the current streak of the given habit.
        :return: the value of the current streak as an integer
        """
        # First, we define when the streak counter should show 0.
        if not self.marked_complete:
            current_streak = 0
        elif self.marked_complete[-1] != date.today():
            current_streak = 0

        # Now let's calculate the streak if there is any.
        else:
            current_date = date.today()
            current_streak = 0
            while current_streak < len(self.marked_complete) and current_date - timedelta(
                    days=current_streak) == self.marked_complete[-(current_streak + 1)]:
                current_streak += 1
                current_streak = int(current_streak)
        return current_streak

    def calculate_total_resisted(self):
        """
        Calculates the total number of days the user resisted performing the habit.
        :return: the value of the total number of innocent days as an integer
        """
        time_difference = datetime.now().date() - self.gen_date
        days_with_data = time_difference.days + 1
        total_completed = self.calculate_total_completed()
        total_not_completed = days_with_data - total_completed
        total_not_completed = int(total_not_completed)
        return total_not_completed

    def calculate_resistance_ratio(self):
        """
        Calculates the ratio of innocent and guilty days.
        :return: a string with the ratio expressed as a string in percentages
        """
        total_resisted = self.calculate_total_resisted()
        time_difference = datetime.now().date() - self.gen_date
        days_with_data = time_difference.days + 1
        resistance_ratio = "{:.2f}%".format((total_resisted / days_with_data) * 100)
        return resistance_ratio

    def calculate_longest_historical_streak(self):
        """
        Calculates the longest streak the user had for the particular habit.
        :return: the value of the longest streak as an integer
        """
        longest_streak = 0
        current_streak = 0
        last_date = None
        for completion_date in reversed(self.marked_complete):
            # Now let's check if the current date is consecutive to the previous one.
            if last_date is not None and last_date - timedelta(days=1) == completion_date:
                current_streak += 1
            else:
                # Reset the streak if it is not consecutive.
                current_streak = 1
            # Update the longest streak if needed.
            longest_streak = max(longest_streak, current_streak)
            last_date = completion_date
        longest_streak = int(longest_streak)
        return longest_streak

    def calculate_average_streak_length(self):
        """
        Calculates the average length of completed streaks for the habit.
        Returns: the average length of completed streaks, considering consecutive days of completion, as a float
        """
        completed_streak_lengths = []
        current_streak = 0
        last_date = None
        for completion_date in reversed(self.marked_complete):
            # Now let's check if the current date is consecutive to the previous one.
            if last_date is not None and last_date - timedelta(days=1) == completion_date:
                current_streak += 1
            else:
                # If there is a gap, consider the current streak completed.
                if current_streak > 0:
                    completed_streak_lengths.append(current_streak)
                # Start a new streak.
                current_streak = 1
            last_date = completion_date
        # If there is a streak ongoing at the end of the loop, consider it completed.
        if current_streak > 0:
            completed_streak_lengths.append(current_streak)
        average_streak = (
                sum(completed_streak_lengths) / len(completed_streak_lengths)
        ) if completed_streak_lengths else 0
        average_streak = round(average_streak, 2)
        return average_streak


class WeeklyHabit(Habit):
    def __init__(self, name="", descr="", gen_date=date.today()):
        super().__init__(name, descr, gen_date, periodicity="Weekly")

    def mark_complete(self, db, mark_date=None):
        """
        Marks the habit as complete for the specific week.
        :param db: The database connection where the marking of the habit will be stores
        :param mark_date: the date on which to mark the habit as complete
        """
        if mark_date is None:
            mark_date = date.today()
        # For marking weekly habits complete, we anchor the completion to the first day of the period
        week_start = mark_date - timedelta(days=mark_date.weekday())
        if week_start not in self.marked_complete:
            self.marked_complete.append(week_start)
        if mark_date != date.today() and mark_date < self.gen_date:
            self.gen_date = mark_date
        self.update_gen_date(db, self.gen_date)
        self.marked_complete.sort()

    def calculate_current_streak(self):
        """
        Calculates the current streak of the given weekly habit.
        :return: the value of the current streak as an integer
        """
        current_streak = 0
        if not self.marked_complete:
            pass
        elif self.marked_complete[-1] != (date.today() - timedelta(days=date.today().weekday())):
            current_streak = 0
        # Now let's calculate the streak if there is any.
        else:
            current_week_start = date.today() - timedelta(days=date.today().weekday())
            current_streak = 0
            while (
                    current_streak < len(self.marked_complete)
                    and current_week_start == self.marked_complete[-(current_streak + 1)]
            ):
                current_streak += 1
                # Subtracting 7 days from the datetime object
                current_week_start -= timedelta(days=7)
        current_streak = int(current_streak)
        return current_streak

    def calculate_total_resisted(self):
        """
        Calculates the total number of weeks the user resisted performing the habit.
        :return: the value of the total number of innocent weeks as an integer
        """
        time_difference = datetime.now().date() - self.gen_date
        # Setting the weeks_with_data variable to 1 in case the creation date is today
        if time_difference.days == 0:
            weeks_with_data = 1
        else:
            weeks_with_data = math.ceil(time_difference.days / 7)
        total_completed = self.calculate_total_completed()
        total_resisted = weeks_with_data - total_completed
        return total_resisted

    def calculate_resistance_ratio(self):
        """
        Calculates the ratio of innocent and guilty weeks.
        :return: a string with the ratio expressed as a string in percentages
        """
        total_resisted = self.calculate_total_resisted()
        time_difference = datetime.now().date() - self.gen_date
        # Setting the weeks_with_data variable to 1 in case the creation date is today
        if time_difference.days == 0:
            weeks_with_data = 1
        else:
            weeks_with_data = math.ceil(time_difference.days / 7)
        resistance_ratio = "{:.2f}%".format((total_resisted / weeks_with_data) * 100)
        return resistance_ratio

    def calculate_longest_historical_streak(self):
        """
        Calculates the longest streak the user had for the particular weekly habit.
        :return: the value of the longest streak as an integer
        """
        longest_streak = 0
        current_streak = 0
        last_week_start = None
        for week_start in reversed(self.marked_complete):
            # Let's check if the current week is consecutive to the previous one.
            if last_week_start is not None and last_week_start - timedelta(weeks=1) == week_start:
                current_streak += 1
            else:
                # Resetting the streak if it is not consecutive
                current_streak = 1
            # Updating the longest streak if needed
            longest_streak = max(longest_streak, current_streak)
            last_week_start = week_start
        longest_streak = int(longest_streak)
        return longest_streak

    def calculate_average_streak_length(self):
        """
        Calculates the average length of completed streaks for the weekly habit.
        Returns: the average length of completed streaks, considering consecutive weeks of completion, as a float
        """
        completed_streak_lengths = []
        current_streak = 0
        last_week_start = None
        for week_start in reversed(self.marked_complete):
            # Now let's check if the current week is consecutive to the previous one.
            if last_week_start is not None and last_week_start - timedelta(days=7) == week_start:
                current_streak += 1
            else:
                # If there is a gap, consider the current streak completed.
                if current_streak > 0:
                    completed_streak_lengths.append(current_streak)
                # Start a new streak.
                current_streak = 1
            last_week_start = week_start
        # If there is a streak ongoing at the end of the loop, consider it completed.
        if current_streak > 0:
            completed_streak_lengths.append(current_streak)
        average_streak = (
                sum(completed_streak_lengths) / len(completed_streak_lengths)
        ) if completed_streak_lengths else 0
        average_streak = round(average_streak, 2)
        return average_streak


class MonthlyHabit(Habit):
    def __init__(self, name="", descr="", gen_date=date.today()):
        super().__init__(name, descr, gen_date, periodicity="Monthly")

    def mark_complete(self, db, mark_date=None):
        """
        Marks the habit as complete for the month.
        :param db: The database connection where the marking of the habit will be stores
        :param mark_date: the date on which to mark the habit as complete
        """
        if mark_date is None:
            mark_date = date.today()
        # For marking monthly habits complete, we anchor the completion to the first day of the month.
        month_start = (mark_date.replace(day=1))
        if month_start not in self.marked_complete:
            self.marked_complete.append(month_start)
        self.marked_complete.sort()
        if mark_date != date.today() and mark_date < self.gen_date:
            self.gen_date = mark_date
        self.update_gen_date(db, self.gen_date)

    def calculate_current_streak(self):
        """
        Calculates the current streak of the given monthly habit.
        :return: the value of the current streak as an integer
        """
        current_streak = 0
        if not self.marked_complete:
            pass
        elif self.marked_complete[-1] != (date.today().replace(day=1)):
            current_streak = 0
        # Now let's calculate the streak if there is any.
        else:
            current_month_start = date.today().replace(day=1)
            current_streak = 0
            while (
                    current_streak < len(self.marked_complete)
                    and current_month_start == self.marked_complete[-(current_streak + 1)]
            ):
                current_streak += 1
                # Subtracting 1 month from the datetime object held by the variable current_month_start
                current_month_start -= timedelta(days=current_month_start.day)
        current_streak = int(current_streak)
        return current_streak

    def calculate_total_resisted(self):
        """
        Calculates the total number of months when the user resisted performing the habit.
        :return: the value of the total number of innocent months as an integer
        """
        months_with_data = (
                (datetime.now().year - self.gen_date.year) * 12 +
                datetime.now().month - self.gen_date.month + 1
        )
        total_completed = self.calculate_total_completed()
        total_resisted = months_with_data - total_completed
        return total_resisted

    def calculate_resistance_ratio(self):
        """
        Calculates the ratio of innocent and guilty weeks.
        :return: a string with the ratio expressed as a string in percentages
        """
        total_resisted = self.calculate_total_resisted()
        months_with_data = (
                (datetime.now().year - self.gen_date.year) * 12 +
                datetime.now().month - self.gen_date.month + 1
        )
        resistance_ratio = "{:.2f}%".format((total_resisted / months_with_data) * 100)
        return resistance_ratio

    def calculate_longest_historical_streak(self):
        """
        Calculates the longest streak the user had for the particular monthly habit.
        :return: the value of the longest streak as an integer
        """
        longest_streak = 0
        current_streak = 0
        last_month_start = None
        for month_start in reversed(self.marked_complete):
            # Let's check if the current month is consecutive to the previous one.
            if last_month_start is not None and (
                    last_month_start - relativedelta(months=1) == month_start):
                current_streak += 1
            else:
                # Resetting the streak if it is not consecutive
                current_streak = 1
            # Updating the longest streak if needed
            longest_streak = max(longest_streak, current_streak)
            last_month_start = month_start
        longest_streak = int(longest_streak)
        return longest_streak

    def calculate_average_streak_length(self):
        """
        Calculates the average length of completed streaks for the monthly habit.
        Returns: the average length of completed streaks, considering consecutive months of completion, as a float
        """
        completed_streak_lengths = []
        current_streak = 0
        last_month_start = None
        for month_start in reversed(self.marked_complete):
            # Let's check if the current month is consecutive to the previous one.
            if last_month_start is not None and (
                    last_month_start - relativedelta(months=1) == month_start):
                current_streak += 1
            else:
                # If there is a gap, consider the current streak completed.
                if current_streak > 0:
                    completed_streak_lengths.append(current_streak)
                # Start a new streak.
                current_streak = 1
            last_month_start = month_start
        # If there is a streak ongoing at the end of the loop, consider it completed.
        if current_streak > 0:
            completed_streak_lengths.append(current_streak)
        average_streak = (
                sum(completed_streak_lengths) / len(completed_streak_lengths)
        ) if completed_streak_lengths else 0
        average_streak = round(average_streak, 2)
        return average_streak

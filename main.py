import json
import sys
# noinspection PyUnresolvedReferences
from datetime import datetime, timedelta, date
import pandas as pd
import questionary
from dataschema import get_db
# noinspection PyUnresolvedReferences
from habit import Habit, DailyHabit, WeeklyHabit, MonthlyHabit
import logging
# noinspection PyUnresolvedReferences
import dataframe
# noinspection PyUnresolvedReferences
import asyncio

# Setting logging level
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('asyncio').setLevel(logging.WARNING)


# Creating a function for getting a user-input date
def get_date_from_user():
    user_date = None
    provided_year = questionary.text(
        "Enter the year:",
        validate=lambda x: x.isdigit(),
    ).ask()

    provided_month = questionary.text(
        "Enter the month:",
        validate=lambda x: x.isdigit() and 1 <= int(x) <= 12,
    ).ask()
    sajt = 1
    # Introducing a loop for day input to handle exceptions related to different month lengths
    while sajt == 1:
        provided_day = questionary.text(
            "Enter the day:",
            validate=lambda x: x.isdigit() and 1 <= int(x) <= 31,
        ).ask()

        try:
            # Converting the user input into a date object
            user_date = datetime(year=int(provided_year),
                                 month=int(provided_month),
                                 day=int(provided_day)).date()
            # Exiting the loop when a valid date is entered
            sajt = 0
        except ValueError as e:
            print(f"Error: {e}. Please enter a valid date. Think about how many days a month have.")
            continue
    return user_date


def ensure_unique_checkoff_dates(db, habit):
    """
    Ensures the uniqueness of check-off dates for a given habit.
    :param db: An SQLite database connection object
    :param habit: Habit object
    """
    cur = db.cursor()
    try:
        # Retrieving the current check_off_dates for the habit
        cur.execute("SELECT check_off_dates FROM habit WHERE name=?;", (habit.name,))
        result = cur.fetchone()
        if result:
            check_off_dates_str = result[0]
            # Deserializing the current check_off_dates
            check_off_dates = json.loads(check_off_dates_str) if check_off_dates_str else []
            # Ensuring uniqueness of check-off dates
            unique_dates = list(set(check_off_dates))
            if len(unique_dates) != len(check_off_dates):
                # Updating the check_off_dates column in the habit table if duplicates found
                cur.execute("UPDATE habit SET check_off_dates=? WHERE name=?;", (json.dumps(unique_dates), habit.name))
                db.commit()
                print(f"Removed duplicate check-off dates for habit '{habit.name}'.")
    except Exception as e:
        # Logging the exception
        print(f"Error ensuring uniqueness of check-off dates: {e}")
    finally:
        cur.close()


def cli():
    """
    A command-line interface for kicking habits.
    This is the function that lets users view their habits, mark them as done, view data, create new habits,
    and delete habits they do not want to track anymore.
    """
    with get_db() as db:
        # Retrieving all habit data from the database
        habits_data = pd.read_sql_query("SELECT * FROM habit", db)
        habits = []
        for index, row in habits_data.iterrows():
            habit = Habit.create_habit(row['name'], row['descr'], row['gen_date'], row['periodicity'], db=db)
            habits.append(habit)
            # Ensuring uniqueness of check-off dates
            ensure_unique_checkoff_dates(db, habit)

        start = questionary.select("Privacy disclaimer:"
                                   " Like everything, your data is safest when it doesn't exist."
                                   " When Kicking Habits,"
                                   " you are encouraged"
                                   " to replace words directly referring to your reality"
                                   " with words mainly you can associate"
                                   " with the relevant part of your reality."
                                   " Would you like to start the thing now?", choices=["Yes", "Rather not"]).ask()
        if start == "Yes":
            pass
        if start == "Rather not":
            print("Bye-bye.")
            sys.exit()
        stop = False

        while not stop:

            choice = questionary.select("Please do select a menu item.",
                                        choices=["1. My habits", "2. View data", "3. Create new habit",
                                                 "4. Delete habit", "5. Exit"]).ask()

            if choice == "3. Create new habit":
                name = questionary.text("What should be the name of the new habit?").ask()
                descr = questionary.text("Please provide a description of the new habit.").ask()
                start_today = questionary.select(
                    "Do you want to track this habit starting with today?", choices=[
                        "Yes", "No"]).ask()
                # Initializing the variable gen_date with a default value
                if start_today == "Yes":
                    gen_date = datetime.today().date()
                else:
                    "Please enter the date when you want to start the tracking of the habit."
                    gen_date = get_date_from_user()
                periodicity = questionary.select("What is the periodicity of the new habit?",
                                                 choices=["Daily", "Weekly", "Monthly"]).ask()
                habit = Habit.create_habit(name, descr, gen_date, periodicity)
                print(f"Congratulations, you have created a habit with name \"{habit.name}\","
                      f" description \"{habit.descr}\","
                      f" creation date of \"{habit.gen_date}\""
                      f" and periodicity \"{habit.periodicity}\"")
                habit.store(db)

            elif choice == "4. Delete habit":
                # Retrieving the list of existing habits
                habits = pd.read_sql_query("SELECT name FROM habit ORDER BY name", db)

                if habits.empty:
                    print("No habits found that you can delete.")
                else:
                    # Providing an extra option with to go back to the main menu
                    habits_list = habits['name'].tolist()
                    habits_list.append("Go back to main menu")

                    habit_to_delete = questionary.select(
                        "Select the habit to delete:", choices=habits_list).ask()
                    # Checking if the user chose to go back to the main menu
                    if habit_to_delete == "Go back to main menu":
                        # Skipping the rest of the loop and going back to the main menu
                        continue

                    # Confirming the deletion with the user
                    confirm_deletion = questionary.select(
                        f"Are you sure you want to delete the habit '{habit_to_delete}'?", choices=[
                            "Yes", "No"]).ask()
                    if confirm_deletion == "Yes":
                        db.execute("DELETE FROM habit WHERE name=?", (habit_to_delete,))
                        db.commit()
                        print(f"Habit '{habit_to_delete}' has been successfully deleted.")
                    else:
                        print("The deletion process has been terminated.")

            elif choice == "1. My habits":
                # Retrieving the list of currently existing habits
                habits = pd.read_sql_query("SELECT name FROM habit ORDER BY name", db)

                if habits.empty:
                    print("No habits found in the database.")
                else:
                    # Listing the name of habits with providing an extra option to go back to the main menu
                    habits_list = habits['name'].tolist()
                    habits_list.append("Go back to main menu")
                    habit_name_to_view = questionary.select(
                        "Select habit:", choices=habits_list).ask()
                    # Checking if the user chose to go back to the main menu
                    if habit_name_to_view == "Go back to main menu":
                        # Skipping the rest of the loop and going back to the main menu
                        continue
                    habit_to_view = Habit.get_habit_by_name(db, habit_name_to_view)
                    print(habit_to_view.marked_complete)
                    # Displaying stats for the selected habit
                    stats_table = habit_to_view.get_individual_stats()
                    print(stats_table)

                    # Option to mark the habit completed
                    mark_completed = questionary.select(
                        "Would you like to mark the habit completed?", choices=["Yes", "no"]
                    ).ask()

                    if mark_completed == "Yes":
                        is_today_mark = questionary.select(
                            "Do you want to mark this habit done for today?", choices=[
                                "Yes", "No"]).ask()
                        if is_today_mark == "Yes":
                            mark_date = habit_to_view.mark_complete(db)
                        else:
                            print("Please enter the date when you want to mark the habit done.")
                            mark_date = get_date_from_user()
                            mark_date = habit_to_view.mark_complete(db, mark_date)
                        habit_to_view.add_event(db, mark_date)
                        db.commit()
                        print(f"Habit '{habit_name_to_view}' has been sadly marked done.")
                    else:
                        print("The marking process has been officially terminated.")

            elif choice == "2. View data":
                ind_or_agg = questionary.select(
                    "Do you want to see data for all habits or individual habits?", choices=[
                        "1. Data for individual habits", "2. Aggregate stats across all habits"
                    ]).ask()
                if ind_or_agg == "1. Data for individual habits":
                    # Retrieving the list of currently existing habits
                    habits = pd.read_sql_query("SELECT name FROM habit", db)
                    if habits.empty:
                        print("No habits found that you can see data for.")
                    else:
                        habit_name_to_analyze = questionary.select(
                            "Select the habit to view stats for:", choices=habits['name'].tolist()).ask()
                        # Retrieving the corresponding Habit object from the database
                        habit_to_analyze = Habit.get_habit_by_name(db, habit_name_to_analyze)
                        stats_table = habit_to_analyze.get_individual_stats()
                        print(stats_table)
                elif ind_or_agg == "2. Aggregate stats across all habits":
                    aggregate_choice = questionary.select(
                        "Select the data you are interested in.",
                        choices=[
                            "All habits tracked",
                            "All same-periodicity habits tracked",
                            "Longest-run current streak",
                            "Longest-run historical streak",
                            "Shortest and longest average streak",
                            "Lowest and highest resistance ratio"
                        ]
                    ).ask()
                    if aggregate_choice == "All habits tracked":
                        all_habits_df = dataframe.display_all_habits_tracked(db)
                        if all_habits_df is not None:
                            print(all_habits_df)
                        else:
                            print("No habits found in the database.")
                    elif aggregate_choice == "All same-periodicity habits tracked":
                        periodicity = questionary.select(
                            "Select the periodicity type you want to peak into.",
                            choices=["Daily", "Weekly", "Monthly"]
                        ).ask()
                        all_same_period_df = dataframe.display_all_same_periodicity_habits_tracked(db, periodicity)
                        if all_same_period_df is not None:
                            print(all_same_period_df)
                        else:
                            print(f"No {periodicity.lower()} habits found in the database.")
                    elif aggregate_choice == "Longest-run current streak":
                        longest_streak_table = dataframe.calculate_longestrun_current_streak(db)
                        if longest_streak_table is not None:
                            print("The longest-run current streak across all habits is…:")
                            print(longest_streak_table)
                        else:
                            print("No habits found in the database.")
                    elif aggregate_choice == "Longest-run historical streak":
                        longest_historical_streak_table = dataframe.calculate_longest_historical_streak(db)
                        if longest_historical_streak_table is not None:
                            print("The longest-run historical streak across all habits is…")
                            print(longest_historical_streak_table)
                    elif aggregate_choice == "Shortest and longest average streak":
                        lowest_largest_stats_aver_table = dataframe.calculate_lowest_and_largest_average_streak(db)
                        if lowest_largest_stats_aver_table is not None:
                            print("The minimum and maximum values for the average streak are as follows.")
                            print(lowest_largest_stats_aver_table)
                    elif aggregate_choice == "Lowest and highest resistance ratio":
                        lowest_largest_resistance_ratio = dataframe.calculate_lowest_and_highest_resistance_ratio(db)
                        if lowest_largest_resistance_ratio is not None:
                            print("The minimum and maximum values for the average streak are as follows.")
                            print(lowest_largest_resistance_ratio)
            else:
                print("Farewell, my darling.")
                stop = True


if __name__ == '__main__':
    cli()

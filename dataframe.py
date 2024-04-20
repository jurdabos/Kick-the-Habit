import dataschema
import pandas as pd
from habit import Habit


def display_all_habits_tracked(db):
    """
    Retrieves all habits tracked from the database, converts the data to a dataframe, and returns it.
    :param db: an initialized sqlite3 database connection
    :return: returns the habit data with columns for name, description, date of creation, periodicity and stats.
    """
    if db is None:
        print("No database connection.")
        return None
    else:
        # Retrieving all habit data from the database
        habit_data = dataschema.get_habit_data(db, None)
        if habit_data:
            # Initializing an empty list to store individual statistics DataFrame for each habit
            habit_stats = []
            # Iterating over each habit and calculate statistics
            for habit_info in habit_data:
                # Extracting the habit name
                name = habit_info['name']
                # Retrieving the Habit object using the name
                habit = Habit.get_habit_by_name(db, name)
                habit_stat = habit.calc_individual_stats()
                if habit_stat is not None:
                    habit_stats.append(habit_stat)
            # Concatenating individual statistics DataFrames into one DataFrame
            all_habits_df = pd.concat(habit_stats, ignore_index=True)
            return all_habits_df
        else:
            print("No habits found in the database.")
            return None


def display_all_same_periodicity_habits_tracked(db, periodicity):
    """
    Retrieves all habits with the same periodicity tracked, converts the data to a dataframe, and returns it.
    :param db: an initialized sqlite3 database connection
    :param periodicity: the periodicity type (Daily, Weekly or Monthly)
    :return: returns the habit data with columns for name, description, date of creation, periodicity and stats.
    """
    if db is None:
        print("No database connection.")
        return None
    else:
        # Ensuring periodicity input is valid
        if periodicity.lower() not in ["daily", "weekly", "monthly"]:
            print("Invalid periodicity.")
            return None
        # Retrieving habits with the same periodicity from the database
        habit_data = dataschema.get_habit_data(db, None)  # Get all habits
        same_periodicity_habits = [habit for habit in habit_data if habit['periodicity'].lower() == periodicity.lower()]

        if same_periodicity_habits:
            # Convert habit data to DataFrame
            all_same_periodicity_habits_df = pd.DataFrame(same_periodicity_habits)
            return all_same_periodicity_habits_df
        else:
            print(f"No {periodicity.lower()} habits found in the database.")
            return None


def calculate_longestrun_current_streak(db):
    """
    Calculates the currently tracked habit with the largest value in the 'current streak' stats column
    and returns a table containing the name (or names in case of a tie) of the corresponding habit (habits)
    and the 'Current streak' value.
    :param db: an initialized sqlite3 database connection
    :return: DataFrame with columns for name and current streak of the habit(s) with the largest value
    """
    if db is None:
        print("No database connection.")
        return None
    # Retrieving all habit data from the database
    all_habits_df = display_all_habits_tracked(db)
    if all_habits_df is not None and not all_habits_df.empty:
        # Finding the habit(s) with the longest current streak
        max_current_streak = all_habits_df['Current streak'].max()
        longest_streak_table = all_habits_df[all_habits_df['Current streak'] == max_current_streak]
        return longest_streak_table[['Name', 'Current streak']]
    else:
        print("No habits found in the database.")
        return None


def calculate_longest_historical_streak(db):
    """
    Calculates the longest historical streak across all habits.
    :param db: SQLite database connection object.
    :return: Pandas DataFrame containing the longest historical streak for each habit.
    """
    cur = db.cursor()
    try:
        # Fetching all habit names from the database
        cur.execute("SELECT name FROM habit")
        habit_names = cur.fetchall()

        # Initializing variables to track the longest historical streak and its corresponding habit
        max_streak = -1
        max_streak_habits = []

        # Iterating over each habit and calculating its longest historical streak
        for habit_name in habit_names:
            habit = Habit.get_habit_by_name(db, habit_name[0])
            if habit:
                longest_streak = habit.calculate_longest_historical_streak()
                if longest_streak > max_streak:
                    max_streak = longest_streak
                    max_streak_habits = [habit_name[0]]
                elif longest_streak == max_streak:
                    max_streak_habits.append(habit_name[0])
        # Creating a DataFrame to store the result
        longest_streak_df = pd.DataFrame({
            'Name': max_streak_habits,
            'Longest historical streak': [max_streak] * len(max_streak_habits)
        })
        return longest_streak_df
    except Exception as e:
        print(f"Error calculating longest historical streak: {e}")
        # Returning an empty dataframe for graceful error handling
        return pd.DataFrame()
    finally:
        cur.close()


def calculate_lowest_and_largest_average_streak(db):
    """
    Calculates the lowest and largest average streaks across all habits and return them in a DataFrame.
    :param db: The database connection object.
    :return: DataFrame containing habit names, their average streaks, and labels indicating lowest or largest streaks.
    """
    habit_stats = []
    cur = db.cursor()
    try:
        # Fetching all habit names from the database
        cur.execute("SELECT name FROM habit")
        habit_names = cur.fetchall()
        # Iterating over all habits in the database
        for habit_name_tuple in habit_names:
            habit_name = habit_name_tuple[0]
            # Removing parentheses and comma from the habit name
            habit_name_cleaned = habit_name.replace("(", "").replace(")", "").replace(",", "")
            habit = Habit.get_habit_by_name(db, habit_name_cleaned)
            if habit:
                # Calculating the average streak for the habit
                average_streak = habit.calculate_average_streak_length()
                # Appending habit name and its average streak to habit_stats list
                habit_stats.append({'Name': habit_name, 'Average streak': average_streak})
        # Creating DataFrame from the list of dictionaries
        streak_df = pd.DataFrame(habit_stats)
        # Finding habit with the lowest average streak
        lowest_average_streak = streak_df['Average streak'].min()
        lowest_average_streak_habit = streak_df[streak_df['Average streak'] == lowest_average_streak].iloc[0]
        lowest_average_streak_habit['Label'] = 'Lowest'
        # Finding habit with the largest average streak
        largest_average_streak = streak_df['Average streak'].max()
        largest_average_streak_habit = streak_df[streak_df['Average streak'] == largest_average_streak].iloc[0]
        largest_average_streak_habit['Label'] = 'Largest'
        # Concatenating the two rows into a DataFrame
        result_df = pd.concat([lowest_average_streak_habit, largest_average_streak_habit], axis=1).T
        return result_df
    except Exception as e:
        print(f"Error calculating minimum and maximum average streak: {e}")
        # Returning an empty dataframe for graceful error handling
        return pd.DataFrame()
    finally:
        cur.close()


def calculate_lowest_and_highest_resistance_ratio(db_conn_obj):
    """
    Calculates the lowest and highest resistance ratios across all habits and returns them in a DataFrame.
    :param db_conn_obj: The database connection object.
    :return: DataFrame containing habit names, their resistance ratios, and labels indicating lowest or highest ratios.
    """
    resistance_stats = []
    cur = db_conn_obj.cursor()
    try:
        # Fetching all habit names from the database
        cur.execute("SELECT name FROM habit")
        habit_names = cur.fetchall()
        # Iterating over all habits in the database
        for habit_name_tuple in habit_names:
            habit_name = habit_name_tuple[0]
            # Removing parentheses and comma from the habit name
            habit_name_cleaned = habit_name.replace("(", "").replace(")", "").replace(",", "")
            habit = Habit.get_habit_by_name(db_conn_obj, habit_name_cleaned)
            if habit:
                # Calculating the resistance ratio for the habit
                resistance_ratio = habit.calculate_resistance_ratio()
                # Appending habit name and its resistance ratio to resistance_stats list
                resistance_stats.append({'Name': habit_name, 'Resistance ratio': resistance_ratio})
        # Creating DataFrame from the list of dictionaries
        resistance_df = pd.DataFrame(resistance_stats)
        # Finding habit with the lowest resistance ratio
        lowest_resistance_ratio = resistance_df['Resistance ratio'].min()
        lowest_res_ratio_habit = resistance_df[resistance_df['Resistance ratio'] == lowest_resistance_ratio].iloc[0]
        lowest_res_ratio_habit['Label'] = 'Lowest'
        # Finding habit with the highest resistance ratio
        highest_resistance_ratio = resistance_df['Resistance ratio'].max()
        highest_res_ratio_habit = resistance_df[resistance_df['Resistance ratio'] == highest_resistance_ratio].iloc[0]
        highest_res_ratio_habit['Label'] = 'Highest'
        # Concatenating the two rows into a DataFrame
        result_df = pd.concat([lowest_res_ratio_habit, highest_res_ratio_habit], axis=1).T
        return result_df
    except Exception as e:
        print(f"Error calculating minimum and maximum resistance ratio: {e}")
        # Returning an empty DataFrame for graceful error handling
        return pd.DataFrame()
    finally:
        cur.close()

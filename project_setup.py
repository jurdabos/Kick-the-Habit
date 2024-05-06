from datetime import date
from dataschema import get_db, create_table, add_habit_to_db, increment_guilt, get_habit_data, clear_database
from freezegun import freeze_time

fake_today = "2024-04-23"


@freeze_time(fake_today)
def test_current_date():
    assert date.today() == date.fromisoformat(fake_today)


# Function to create the test database and add predefined habits and their check-off dates
def setup_test_database():
    test_db = get_db(name='test.db')
    create_table(test_db)
    # Adding predefined habits
    add_habit_to_db(test_db, name='Swearstorming', descr='Unleashing a torrent of colorful language',
                    gen_date=date.fromisoformat("2024-03-23"), periodicity='Daily')
    add_habit_to_db(test_db, name='Overanalyzing', descr='To analyze sg too much or in too much detail',
                    gen_date=date.fromisoformat("2024-03-23"), periodicity='Daily')
    add_habit_to_db(test_db, name='Binge watching', descr='Viewing many episodes of a TV show in one sitting',
                    gen_date=date.fromisoformat("2024-01-01"), periodicity='Weekly')
    add_habit_to_db(test_db, name='Rushing', descr='Constantly being in a hurry for no good reason',
                    gen_date=date.fromisoformat("2024-01-01"), periodicity='Weekly')
    add_habit_to_db(test_db, name='Procrastipondering', descr='Delaying tasks while pondering over their importance',
                    gen_date=date.fromisoformat("2023-01-01"), periodicity='Monthly')
    # Adding check-off dates for the predefined test habits
    increment_guilt(test_db, name='Swearstorming', event_date="2024-03-23")
    increment_guilt(test_db, name='Swearstorming', event_date="2024-03-24")
    increment_guilt(test_db, name='Swearstorming', event_date="2024-03-25")
    increment_guilt(test_db, name='Swearstorming', event_date="2024-03-26")
    increment_guilt(test_db, name='Swearstorming', event_date="2024-03-27")
    increment_guilt(test_db, name='Swearstorming', event_date="2024-04-23")
    increment_guilt(test_db, name='Overanalyzing', event_date="2024-03-23")
    increment_guilt(test_db, name='Overanalyzing', event_date="2024-04-20")
    increment_guilt(test_db, name='Overanalyzing', event_date="2024-04-21")
    increment_guilt(test_db, name='Overanalyzing', event_date="2024-04-22")
    increment_guilt(test_db, name='Overanalyzing', event_date="2024-04-23")
    increment_guilt(test_db, name='Binge watching', event_date="2024-03-25")
    increment_guilt(test_db, name='Binge watching', event_date="2024-04-22")
    increment_guilt(test_db, name='Rushing', event_date="2024-01-01")
    increment_guilt(test_db, name='Rushing', event_date="2024-01-08")
    increment_guilt(test_db, name='Rushing', event_date="2024-01-15")
    increment_guilt(test_db, name='Rushing', event_date="2024-04-15")
    increment_guilt(test_db, name='Rushing', event_date="2024-04-22")
    increment_guilt(test_db, name='Procrastipondering', event_date="2023-01-01")
    increment_guilt(test_db, name='Procrastipondering', event_date="2023-02-01")
    increment_guilt(test_db, name='Procrastipondering', event_date="2023-03-01")
    increment_guilt(test_db, name='Procrastipondering', event_date="2023-04-01")
    increment_guilt(test_db, name='Procrastipondering', event_date="2023-05-01")
    increment_guilt(test_db, name='Procrastipondering', event_date="2023-06-01")
    increment_guilt(test_db, name='Procrastipondering', event_date="2023-07-01")
    increment_guilt(test_db, name='Procrastipondering', event_date="2023-08-01")
    increment_guilt(test_db, name='Procrastipondering', event_date="2023-09-01")
    increment_guilt(test_db, name='Procrastipondering', event_date="2024-01-01")
    return test_db


# Function to print test habits and their check-off dates in a readable table format
def print_habit_check_off_dates(test_db):
    habits = get_habit_data(test_db, name=None)
    if habits:
        max_name_length = max(len(habit['name']) for habit in habits)
        print("Habit" + " " * (max_name_length - 4) + "\tGen Date\t\t\tCheck-off Dates")
        print("=" * 80)
        for habit in habits:
            check_off_dates = habit['check_off_dates']
            check_off_dates_str = ", ".join([str(each_date) for each_date in check_off_dates])
            print(f"{habit['name']}" +
                  " " * (max_name_length - len(habit['name'])) +
                  f"\t{habit['gen_date']}\t\t{check_off_dates_str}")


# Function to reset the test database by clearing check-off dates
def reset_test_database():
    test_db = get_db(name='test.db')
    clear_database(test_db)
    test_db.close()


# Main function to run setup and print habits
def main():
    test_db = setup_test_database()
    # The next line should be uncommented to clear the check-off dates already added for the test database.
    # reset_test_database()
    print_habit_check_off_dates(test_db)
    test_db.close()


if __name__ == "__main__":
    main()

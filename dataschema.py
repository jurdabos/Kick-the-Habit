# All database connections, loading data etc.
import sqlite3
from datetime import date, datetime
import json
from typing import Optional, Dict, Any


def get_db(name='main.db'):
    """
    Gets an SQLite database connection.
    :param name: The name of the database file (default is 'main.db')
    :return: An SQLite database connection object
    """
    try:
        db = sqlite3.connect(name)
        # print("Database connection successful!")
        create_table(db)
        return db
    except sqlite3.Error as e:
        print("Error connecting to database:", e)
        return None


def create_table(db):
    """
    Creates a table in the database if it does not already exist, and commits the changes.
    :param db: An SQLite database connection object
    """
    cur = db.cursor()
    # Storing 'gen_date' as TEXT in ISO 8601 format
    # Storing 'check_off_dates' as a serialized list
    cur.execute("""CREATE TABLE IF NOT EXISTS habit(
        name TEXT PRIMARY KEY,
        descr TEXT,
        gen_date TEXT,
        periodicity TEXT,
        check_off_dates TEXT DEFAULT '[]');""")

    db.commit()
    cur.close()


def add_habit_to_db(db: sqlite3.Connection, name: str, descr: str, gen_date: date, periodicity: str):
    """
    Adds a habit to the 'habit' table in the database in case it doesn't already exist.
    :param db: An SQLite database connection object
    :param name: Name of the habit as a string
    :param descr: The description of the habit as a string
    :param gen_date: The creation date of the habit as a date object
    :param periodicity: The periodicity of the habit as a string
    """
    cur = db.cursor()
    gen_date_str = gen_date.strftime('%Y-%m-%d') if gen_date else None
    # First check if a habit with the given name already exists
    cur.execute("SELECT COUNT(*) FROM habit WHERE name=?;", (name,))
    count = cur.fetchone()[0]

    if count == 0:
        # The habit does not exist, so we can insert it.
        # Initializing an empty list for check-off dates
        check_off_dates = []
        cur.execute("INSERT INTO habit VALUES (?, ?, ?, ?, ?);",
                    (name, descr, gen_date_str, periodicity, json.dumps(check_off_dates)))
        db.commit()
    else:
        # Habit with the same name already exists, so we will handle this case accordingly.
        print(f"Habit with name '{name}' already exists. Skipping insertion.")

    cur.close()


def increment_guilt(db: sqlite3.Connection, name: str, event_date=None):
    """
    Adds a guilty event to the 'check_off_dates' column.
    :param db: An SQLite database connection object
    :param name: Name of the habit
    :param event_date: Date of the event (default is today)
    """
    cur = db.cursor()
    if not event_date:
        event_date = str(date.today())
    try:
        # Retrieving the current check_off_dates for the habit
        cur.execute("SELECT check_off_dates FROM habit WHERE name=?;", (name,))
        check_off_dates_str = cur.fetchone()[0]
        # Deserializing the current check_off_dates
        check_off_dates = json.loads(check_off_dates_str) if check_off_dates_str else []
        if event_date not in check_off_dates:
            # Adding the new event_date to the list only if it's not already present
            check_off_dates.append(event_date)
            # Updating the check_off_dates column in the habit table
            cur.execute("UPDATE habit SET check_off_dates=? WHERE name=?;", (json.dumps(check_off_dates), name))
            db.commit()
        else:
            print(f"The date {event_date} has been already marked for habit {name}. Skipping insertion.")

    except Exception as e:
        # Logging the exception
        print(f"Error updating check_off_dates: {e}")
    finally:
        cur.close()


def get_habit_data(db_conn_obj_schema_ghb: sqlite3.Connection, name: Optional[str]):
    """
    Retrieves habit data from the table in the database.
    :param db_conn_obj_schema_ghb: An SQLite database connection object
    :param name: Name of the habit
    :return: List of dictionaries containing habit data (name, descr, gen_date, periodicity, check_off_dates)
    """
    # Check if db is a valid database connection.
    if not isinstance(db_conn_obj_schema_ghb, sqlite3.Connection):
        raise ValueError("Invalid database connection")
    cur = db_conn_obj_schema_ghb.cursor()
    try:
        if name is None:
            # If name is None, retrieve all habits
            query = "SELECT name, descr, gen_date, periodicity, check_off_dates FROM habit;"
            cur.execute(query)
        else:
            # Retrieve the habit by name
            if not isinstance(name, str):
                raise ValueError("Invalid name input")
            query = "SELECT name, descr, gen_date, periodicity, check_off_dates FROM habit WHERE name=?;"
            cur.execute(query, (name,))
        columns = [col[0] for col in cur.description]
        habit_data = []
        for row in cur.fetchall():
            data_dict: Dict[str, Any] = dict(zip(columns, row))
            # Converting gen_date to date object
            data_dict['gen_date'] = datetime.strptime(data_dict['gen_date'], '%Y-%m-%d').date()
            data_dict['check_off_dates'] = json.loads(data_dict['check_off_dates'])
            habit_data.append(data_dict)
        return habit_data

    except sqlite3.Error as e:
        # Logging the exception
        print(f"Error executing SQL query: {e}")
        return None

    finally:
        cur.close()

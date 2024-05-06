# Overview

Kick the Habit is a habit-tracking app tailored to tracking and kicking our bad habits. It is possible to create and remove habits in the programme, and you can check off a habit after completing the associated activity. You can look at stats about your success in or struggle with kicking your bad habits.

## How does it work?

It is a pure Python project developed in Pycharm.
Launch it by navigating to the project folder and typing python main.py, then use the arrow keys to select menu items.
First, create a habit under the menu item 'Create new habit'.
After this, you will be able to mark the habit completed and see individual stats related to it under menu item 'My habits'. You can delete habits you are not interested in anymore in menu item no. 4 'Delete habit'. If you choose '2. View data', you will be able to see extra aggregate stats pertaining to all habits currently stats.

## The basic building blocks

The core component of the application is a command-line interface. The database connection is implemented using sqlite3.

The application uses the datetime module to identify the date when a habit is marked done in case the user chooses to mark it done for the given day. It also offers an opportunity to check off habits “after the fact”, in case the user forgets to mark an activity completed on the day it is done.

## Installation

```shell
pip install -r requirements.txt
```

## How to use it?

Note: Make sure you have Python 3.12 installed on your system.
Navigate to the project directory, then launch
```shell
python main.py
```
and choose from the menu options.

## Tests
Navigate to the project library, then run the test script with the following command.
```shell
python test_dataframe.py
```
This launches all the tests implemented for the project, both for the analytics module, both for the database connection.
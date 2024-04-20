# Habit-tracking app

With this app, you can define your bad habits to track. It is possible to remove habits that are not interesting anymore, and you can check off a habit after completing the associated activity. The programme lets you have a look at stats about your success in or struggle with kicking your bad habits.

## How does it work?

It is a pure Python project developed in Pycharm. It is is built using Python version 3.12, including a main.py, which is the main entry point for the application, a habit.py file with the Habit class that lets users create habit instances and is also used to calculate stats for individual habits, test files for validation, a dataframe.py for scalable statistics across habits, an init.py file for logging set-up, and, finally, this READme.md file to document the project. It uses venv to isolate project dependencies.
Launch it by typing python main.py, then use the arrows to select menu items, and type in the names and descriptions for the habits you want to add to track.

## The basic building blocks

The core component of the application is a command-line interface function. This handles the commands selected by the user through the interface, i. e. all the habit creation, deletion and retrieval activities. The cli function is linked to a database holding the habits. Through the interface, it is also possible to see stats that pertain to all the habits taken together, e. g. longest current guilty streak across habits, longest historical guilty streak across all habits and total average streak for all the habits in the program.

A Habit class has been created for operations regarding single habit objects. A habit has attributes such as name, task specification (description), creation date and periodicity. The app creates a list for each habit containing all the dates when it is marked complete. This list is originally empty, then it might get populated with dates. There are several methods associated with this class. A habit can be completed, or checked off, by a user at any time. The application uses the datetime module to identify the date when a habit is marked done in case the user chooses to mark it done for the given day. It also offers an opportunity to check off habits “after the fact”, in case the user forgets to mark an activity completed on the day it is done. The mark_complete method adds a date to the list of dates maintained by the class, and the list gets updated by the sort method. Calling the get_individual_stats method creates a dataframe through the calc_individual_stats function with up-to-date analytics insights such as current streak, longest streak, average streak etc. based on the above list and the today() method from the datetime module.

## Installation

```shell
pip install -r requirements.txt
```

## How to use it?

Note: Make sure you have Python 3.12 installed on your system.

Launch
```shell
 main.py
```
then choose from the menu options.

## Tests
The program will come with tests soon. :)
You will be able to run them by navigating to the project library, then running the test script.
```shell
pytest .
```
from peewee import DatabaseError, OperationalError
from work_log_db_models import Entry
import sys


class WorkLog():
    def __init__(self):
        try:
            Entry.create_table()
            print('Creating new database')
        except OperationalError:
            print('Using existing database')
            pass
        self.log_data = []

    def get_data(self):
        try:
            self.log_data = Entry.select()
        except DatabaseError as e:
            print('Database Error: ', e)

    def quit(self):
        sys.exit(0)

    def get_input(self, display_string, numerical_choices=None):
        possible_choices = self.get_letter_choice_list(display_string)
        if numerical_choices is not None:
            possible_choices = possible_choices + \
                               self.get_number_choice_list(numerical_choices)

        valid_chosen = None
        while valid_chosen is None:
            choice = input(display_string)
            valid_chosen = self.validate_input(choice, possible_choices)

            if valid_chosen is not None:
                return valid_chosen
            else:
                print('Invalid choice try again')

    def get_letter_choice_list(self, display_string):
        possible_choices = []
        index = 0
        for letter in display_string:
            if letter == '(':
                possible_choices.append(display_string[index + 1].lower())
            index += 1
        return possible_choices

    def get_number_choice_list(self, numerical_choices):
        indices = []
        for i in range(0, numerical_choices.__len__()):
            indices.append(i)
        return indices

    def validate_input(self, choice, possible_choices):
        try:
            choice = int(choice)
        except ValueError:
            choice = choice.lower()
        if choice in possible_choices:
            return choice
        else:
            return None

    def main_menu(self):
        self.get_data()
        while 1:
            print(' -- Main Menu -- ')
            menu_choice = self.get_input('(V)iew, (N)ew, (S)earch, (Q)uit ')
            if menu_choice == 'v':
                self.show_log_pretty(show_index=True)
            if menu_choice == 'q':
                self.quit()
            if menu_choice == 's':
                self.search()
            if menu_choice == 'n':
                self.new_entry()

    def insert_new_entry(self, entry):
        try:
            new_entry = Entry.create(
                user=entry['user'],
                task_name=entry['task_name'],
                time_spent=entry['time_spent'],
                notes=entry['notes']
            )
            return new_entry.id
        except DatabaseError as e:
            print('DatabaseError saving new entry.', e)
            return 0
        except KeyError as e:
            print('KeyError saving new entry.', e)
            return 0
        except TypeError as e:
            print('TypeError saving new entry.', e)
            return 0

    def new_entry(self):
        new_entry = {}
        new_entry['user'] = input('Please enter a user name: ')
        new_entry['task_name'] = input('Please enter a task name: ')
        time_is_added = 0
        while time_is_added == 0:
            time_spent = input('Please enter time spent: ')
            try:
                new_entry['time_spent'] = int(time_spent)
                time_is_added = 1
            except ValueError:
                print('Please enter an integer ')
        new_entry['notes'] = input('Please enter your notes: ')
        new_entry_insert = self.insert_new_entry(new_entry)
        if new_entry_insert != 0:
            print('Added: ')
            print(self.show_entry_pretty(new_entry_insert))

    def search(self):
        self.get_data()
        choice = self.get_input('Search by (U)ser, (D)ate, (T)ime spent, '
                                '(E)xact, (P)attern ')
        search_results = []

        if choice == 'u':
            # As a user of the script, if finding by employee, I should be
            # presented with a list of employees with
            # entries and be able to choose one to see entries from.
            user_list = [x.user for x in self.log_data]
            user_list = sorted(set(user_list))
            for single_user in user_list:
                print(user_list.index(single_user), single_user)
            user_chosen = self.get_input(
                'Please enter the number of user  to search or (M)anual: ',
                user_list)
            if user_chosen == 'm':
                user_chosen = input('Enter exact user name to search: ')
            else:
                user_chosen = user_list[user_chosen]
            search_results = self.get_user_search_results(user_chosen)

        if choice == 'd':
            # When finding by date, I should be presented with a list of dates
            # with entries and be able to choose one to see entries from.
            dates_list = [x.date for x in self.log_data]
            dates_list = sorted(set(dates_list))
            for single_date in dates_list:
                print(dates_list.index(single_date), single_date)
            date_chosen = dates_list[self.get_input(
                'Enter the number of date: ', dates_list)]
            search_results = self.get_date_search_results(date_chosen)

        elif choice == 't':
            # When finding by time spent, I should be allowed to enter the
            # number of minutes a task took and be able to choose one to see
            # entries from.
            valid_time = 0
            search_time_spent = 0
            while valid_time == 0:
                search_time_spent = input('Enter time spent (mins): ')
                try:
                    search_time_spent = int(search_time_spent)
                    valid_time = 1
                except ValueError:
                    print('Please enter an integer: ')
            search_results = self.get_time_spent_search_results(
                search_time_spent)

        elif choice == 'e':
            # When finding by an exact string, I should be allowed to enter a
            # string and then be presented with entries containing that string
            # in the task name or notes.
            search_string = input('Enter search string: ')
            search_results = self.get_exact_search_results(search_string)

        elif choice == 'p':
            # When finding by a pattern, I should be allowed to enter a
            # regular expression and then be presented with entries matching
            # that pattern in their task name or notes.
            search_regex = input('Enter search pattern: ')
            search_results = self.get_pattern_search_results(search_regex)

        self.print_results(search_results)

    def get_user_search_results(self, user_chosen):
        search_results = Entry.select().where(
                Entry.user == user_chosen)
        return search_results

    def get_date_search_results(self, date_chosen):
        search_results = Entry.select().where(
            (Entry.date.year == date_chosen.year) &
            (Entry.date.month == date_chosen.month) &
            (Entry.date.day == date_chosen.day))
        return search_results

    def get_time_spent_search_results(self, search_time_spent):
        search_results = Entry.select().where(
            Entry.time_spent == search_time_spent)
        return search_results

    def get_exact_search_results(self, search_string):
        search_results = Entry.select().where(
            (Entry.task_name.contains(search_string)) |
            (Entry.notes.contains(search_string)))
        return search_results

    def get_pattern_search_results(self, search_regex):
        search_results = Entry.select().where(
            (Entry.task_name.regexp(search_regex)) |
            (Entry.notes.regexp(search_regex)))
        return search_results

    def print_results(self, results_list):
        list_length = results_list.__len__()
        if list_length == 0:
            print('No results')
        if list_length == 1:
            print(self.show_entry_pretty(results_list[0]))
        else:
            for entry in results_list:
                print(self.show_entry_pretty(entry))

    def show_log_pretty(self, show_index=None):
        self.get_data()
        if show_index is None:
            for entry in self.log_data:
                print(
                    'Date: ', entry.date,
                    'User: ', entry.user,
                    'Task Name: ', entry.task_name,
                    'Time Spent: ', entry.time_spent,
                    'Notes: ', entry.notes
                )
        else:
            for entry in self.log_data:
                print(
                    'Id: ', entry.id,
                    'Date: ', entry.date,
                    'User: ', entry.user,
                    'Task Name: ', entry.task_name,
                    'Time Spent: ', entry.time_spent,
                    'Notes: ', entry.notes
                )

    def show_entry_pretty(self, entry_id):
        if type(entry_id) == int:
            entry = Entry.select().where(
                Entry.id == entry_id).first()
        else:
            entry = entry_id
        pretty_entry = 'Date: {} User: {} Task Name: {} ' \
                       'Time Spent: {} Notes: {}'.format(
                            entry.date,
                            entry.user,
                            entry.task_name,
                            entry.time_spent,
                            entry.notes)
        return pretty_entry

    def run(self):
        self.get_data()
        self.main_menu()


if __name__ == '__main__':
    worklog = WorkLog()
    worklog.run()

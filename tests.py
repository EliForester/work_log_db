import unittest.mock
from unittest import TestCase
import work_log_db
from work_log_db_models import Entry
import io


class TestWorkLog(TestCase):

    def setUp(self):
        self.test_worklog = work_log_db.WorkLog()

    def tearDown(self):
        # If someone named Ahab joins the company this will be trouble
        # Maybe reassign test entry to some random data each time
        delete_test_data = Entry.delete().where(Entry.user == 'Ahab')
        delete_test_data.execute()

    def test_number_list(self):
        test_list = [0, 1, 2, 3]
        self.assertEqual(
            self.test_worklog.get_number_choice_list(test_list),
            test_list,
            True)

    def test_string_list(self):
        test_string = '(X) or (D) or P'
        self.assertEqual(
            self.test_worklog.get_letter_choice_list(test_string),
            ['x', 'd'],
            True)

    def test_validate_input(self):
        good_choices = ['X', 'x', 1]
        bad_choices = ['h', 'v', 2]
        possible_test_choices = ['x', 'y', 'z', 1]

        for test_choice in good_choices:
            if type(test_choice) is int:
                validate_against = test_choice
            else:
                validate_against = test_choice.lower()
            self.assertEqual(
                self.test_worklog.validate_input(
                    test_choice,
                    possible_test_choices),
                validate_against)

        for test_choice in bad_choices:
            self.assertIs(
                self.test_worklog.validate_input(
                    test_choice,
                    possible_test_choices),
                None
            )

    def test_show_entry_pretty(self):

        class TestEntry:
            date = '2017-6-1'
            user = 'Llewelyn'
            task_name = 'Gettin'
            time_spent = 3
            notes = 'At the gettin place'

        test_entry = TestEntry
        validate_string = 'Date: 2017-6-1 User: Llewelyn Task Name: Gettin ' \
                          'Time Spent: 3 Notes: At the gettin place'
        self.assertEqual(
            self.test_worklog.show_entry_pretty(test_entry),
            validate_string
        )

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_print_results(self, mock_stdout):

        class TestEntry:
            date = '2017-6-1'
            user = 'Llewelyn'
            task_name = 'Gettin'
            time_spent = 3
            notes = 'At the gettin place'

        test_entry1 = TestEntry
        test_entry2 = TestEntry
        test_results_list = [test_entry1, test_entry2]

        validate_string = 'Date: 2017-6-1 User: Llewelyn Task Name: Gettin ' \
                          'Time Spent: 3 Notes: At the gettin place\n' \
                          'Date: 2017-6-1 User: Llewelyn Task Name: Gettin ' \
                          'Time Spent: 3 Notes: At the gettin place\n'

        self.test_worklog.print_results(test_results_list)

        self.assertEqual(
            mock_stdout.getvalue(),
            validate_string
        )

    def test_new_entry(self):
        print('Test insert_new_entry')
        entry = {'user': 'Ahab',
                 'task_name': 'Whalewatching',
                 'time_spent': 999,
                 'notes': 'Test data: delete if exists'}

        self.assertNotEqual(
            self.test_worklog.insert_new_entry(entry),
            0
        )

        self.assertEqual(
            self.test_worklog.insert_new_entry('xyz'),
            0
        )

    def add_test_db_entry(self):
        entry = {'user': 'Ahab',
                 'task_name': 'Whalewatching',
                 'time_spent': 999,
                 'notes': 'Test data, delete if exists'}

        id = self.test_worklog.insert_new_entry(entry)
        return id

    def test_get_data(self):
        self.assertIsNone(
            self.test_worklog.get_data()
        )

    @unittest.mock.patch('builtins.input', return_value='q')
    def test_main_menu_quit(self, input):
        with self.assertRaises(SystemExit) as exiter:
            self.test_worklog.main_menu(),

        self.assertEqual(exiter.exception.code, 0)

    @unittest.mock.patch('builtins.input', return_value='x')
    def test_get_input(self, input):
        test_string = '(X) (D) P'
        validate_string = 'x'

        self.assertEqual(
            self.test_worklog.get_input(test_string),
            validate_string
        )

    def test_search_user(self):
        print('Test get_user_search_results')
        self.add_test_db_entry()
        data = self.test_worklog.get_user_search_results('Ahab')
        self.assertEqual(data[0].user, 'Ahab')

    def test_search_time(self):
        print('Test get_time_spent_search')
        self.add_test_db_entry()
        data = self.test_worklog.get_time_spent_search_results(999)
        self.assertEqual(data[0].time_spent, 999)

    def test_search_exact(self):
        print('Test get_exact_search_results')
        self.add_test_db_entry()
        data = self.test_worklog.get_exact_search_results('watching')
        self.assertEqual(data[0].task_name, 'Whalewatching')

    def test_search_pattern(self):
        print('Test get_pattern_search_results')
        self.add_test_db_entry()
        data = self.test_worklog.get_pattern_search_results('watching')
        self.assertEqual(data[0].task_name, 'Whalewatching')


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/python3
import glob
import os
import shutil
import optparse
import re
from typing import List

from Database import Database
from colorama import Fore

from FormatError import FormatError


class Cli:
    MESSAGE_NORMAL = 0
    MESSAGE_IMP = 1
    MESSAGE_ERR = 2

    def __init__(self):
        """
        Gui class constructor. Initialize database file name and database object.
        """
        self._database_file = None
        self._database = Database()
        self.work_path = os.path.join('.', 'workDir')

        self._parser = optparse.OptionParser('Usage: ./Cli.py  -a | -g | -d ID | -s STRING [-f FILE] \nExamples:\n'
                                             './Cli.py -a\n'
                                             './Cli.py -g\n'
                                             './Cli.py -d 42\n'
                                             './Cli.py -s [bear]\n'
                                             './Cli.py -s bear -f database.yml')

        self._parser.add_option('-a', '--add', default=False,
                                action="store_true", dest="add_record",
                                help="Run the process of adding a record into database")

        self._parser.add_option('-d', '--delete', type='string',
                                action="store", dest="delete_id",
                                help="Delete a database record with the passed ID")

        self._parser.add_option('-f', '--file', type='string',
                                action="store", dest="database_file",
                                help="Open database in the file, if empty the first yaml file in the directory is used")

        self._parser.add_option('-g', '--graph', default=False,
                                action="store_true", dest="make_graph",
                                help="Create a graph of the database")

        self._parser.add_option('-s', '--search', type='string',
                                action="store", dest="search_string",
                                help="Search for this string in the database, if empty all records are printed")

        self._options, _ = self._parser.parse_args()
        option_combination = [self._options.add_record, self._options.delete_id,
                              self._options.make_graph, self._options.search_string]
        option_combination = [1 for o in option_combination if o]
        if len(option_combination) > 1:
            self._parser.error('Only one option can be used at a time')
        if not option_combination:
            self._parser.error('At least one option is required')

    @staticmethod
    def print_record(records) -> None:
        """
        Nice print the passed list of records.
        :param records: List of yaml records
        :return: None
        """
        for record in records:
            for name, values in record.items():
                print('\n' + Fore.GREEN + str(name) + Fore.RESET)
                for attribute, content in values.items():
                    if attribute in ['email', 'linkto']:
                        if attribute == 'email':
                            if content:
                                print('\t' + 'e-mails:')
                            else:
                                print('\t' + 'e-mails: -')
                        else:
                            if content:
                                print('\t' + 'link to:')
                            else:
                                print('\t' + 'link to: -')
                        if content:
                            for item in content:
                                print('\t\t' + Fore.YELLOW + str(item) + Fore.RESET)
                    else:
                        print('\t' + str(attribute) + ': ' + (
                            '-' if not content else Fore.LIGHTBLUE_EX + str(content) + Fore.RESET))

    @staticmethod
    def print_message(message: str, kind: int) -> None:
        """
        Print a nice looking message on the screen.
        :param message:
        :param kind: One of MESSAGE_NORMAL,IMP,ERR if the message should be an error, normal or important.
        :return: None
        """
        newline = ''
        # If the message begins with a new line add it before the ##
        if message[0] == '\n':
            newline = '\n'
            message = message[1:]
        if kind == Cli.MESSAGE_ERR:
            print(Fore.RED + newline + '## ' + str(message) + Fore.RESET)
        elif kind == Cli.MESSAGE_IMP:
            print(Fore.CYAN + newline + '## ' + str(message) + Fore.RESET)
        else:
            print(newline + '## ' + str(message))

    def search(self) -> None:
        """
        Run database search and print results.
        :return: None
        """
        self.print_message('Searching for: ' + self._options.search_string, Cli.MESSAGE_IMP)
        records = self._database.find(self._options.search_string)
        self.print_record(records)
        self.print_message('\nFound: ' + str(len(records)) + ' database records', Cli.MESSAGE_IMP)

    def _get_linkto(self) -> List[str]:
        """
        Return a list of linkto database records, ask the user to provide them.
        :return: Return a list of linkto database records, ask the user to provide them.
        """
        link_list = []
        print('This account links to:')
        while self.confirm('Add another?'):
            link_list.append(str(input('Record: ')).lstrip().rstrip())
        return link_list

    @staticmethod
    def _get_email() -> str:
        """
        Ask the user for a valid e-mail address and return it.
        :return: str, a valid e-mail address.
        """
        email = ''
        while not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            email = str(input('Address: ')).lstrip().rstrip()
        return email

    @staticmethod
    def _get_password() -> str:
        """
        Ask the user for a valid password and return it.
        :return: str, a valid password.
        """
        password = ''
        while not password:
            password = str(input('Password: ')).lstrip().rstrip()
        return password

    @staticmethod
    def _get_simple_attribute(attribute: str) -> str:
        """
        Ask the user for an attribute and return it.
        :return: str, the attribute from user.
        """
        return str(input(attribute + ': ')).lstrip().rstrip()

    def add(self) -> None:
        """
        Add a new record into the database, ask the user for details.
        :return: None
        """
        record_id = self._database.get_new_id()
        self.print_message('\nAdd new record ID: ' + str(record_id), Cli.MESSAGE_IMP)
        self.print_message('Select category:', Cli.MESSAGE_IMP)
        print('Email -> "e"')
        print('Website -> "w')
        print('Company -> "c"')
        selection = None
        while selection not in ['e', 'w', 'c']:
            selection = str(input('Category [e/w/c]: '))

        # Add an e-mail
        if selection == 'e':
            self.print_message('\nAdding a new e-mail', Cli.MESSAGE_IMP)
            email = self._get_email()
            login = email.split('@')[0]
            password = self._get_password()
            question = self._get_simple_attribute('Security question')
            linktos = self._get_linkto()
            notes = self._get_simple_attribute('Additional notes')
            self.print_message('\nSaving new record', Cli.MESSAGE_IMP)
            # Record example
            # {'whitebear@volny.cz': {'id': 3, 'linkto': ['bear@gmail.com', 'white@gmail.com'], 'login': 'whitebear',
            # 'notes': None, 'password': 'thepassword', 'question': 'what question?'}}
            new_record = {email: {'id': record_id, 'linkto': (linktos if linktos else None), 'login': login,
                                  'notes': (notes if notes else None), 'password': password,
                                  'question': (question if question else None)}}
            if self._database.add('emails', new_record):
                self.print_message('Record added, database saved', Cli.MESSAGE_IMP)

        # Add a website
        if selection == 'w':
            pass

        # Add a company
        if selection == 'c':
            pass

        # Save to disk and replace
        if not self._replace_database():
            self.print_message('Error replacing database', cli.MESSAGE_ERR)

    def delete(self) -> None:
        """
        Remove a record from database based on ID. Get input from the user.
        :return: None
        """
        self.print_message('\nRemove record ID: ' + str(self._options.delete_id) + ':', Cli.MESSAGE_IMP)
        record = self._database.find_id(int(self._options.delete_id))
        self.print_record([record])
        if self.confirm('\n Are you sure?'):
            self.print_message('Removing', Cli.MESSAGE_NORMAL)
            if self._database.delete(int(self._options.delete_id)):
                self.print_message('Record deleted, database saved', Cli.MESSAGE_IMP)
                if not self._replace_database():
                    self.print_message('Error replacing database', cli.MESSAGE_ERR)
        else:
            self.print_message('Deletion canceled', Cli.MESSAGE_IMP)

    def graph(self) -> None:
        """
        Create a graph of the database. Back up old version of the graph if exists in the directory.
        :return: None
        """
        self.print_message('Creating database graph', Cli.MESSAGE_IMP)
        # Rename previous graph
        file_path = os.path.join('.', 'graph.pdf')
        if os.path.exists(file_path):
            self.print_message('Backing up previous graph', Cli.MESSAGE_IMP)
            os.rename(file_path, os.path.join('.', 'graph.old.pdf'))
        self._database.graph('graph')
        # Remove intermediate file
        os.remove(os.path.join('.', 'graph'))
        self.print_message('Graph saved: ' + str(os.path.join('.', 'graph.pdf')), Cli.MESSAGE_IMP)

    def _replace_database(self) -> bool:
        """
        Replace original database file with the valid workingCopy database after transactions.
        :return: True if replaced successfully.
        """
        os.replace(os.path.join(self.work_path, 'workCopy.yml'), os.path.join('.', self._database_file))
        self.print_message(str(self._database_file + ' replaced successfully'), Cli.MESSAGE_IMP)
        return True

    @staticmethod
    def confirm(prompt: str) -> bool:
        """
        Ask the user for confirmation, return True of False.
        :param prompt: str, Display this prompt.
        :return: True if the user answered yes.
        """
        answer = None
        while answer not in ['y', 'Y', 'n', 'N']:
            answer = str(input(prompt + ' [y/n]: '))
            if answer in ['y', 'Y']:
                return True
            if answer in ['n', 'N']:
                return False

    def run(self) -> None:
        """
        This method begins the user interaction with the database.
        :return: None
        """
        if self._options.database_file:
            self._database_file = self._options.database_file
        else:
            yml_files = glob.glob('*.yml')
            if yml_files:
                self._database_file = yml_files[0]
                self.print_message('Using database: ' + str(self._database_file), Cli.MESSAGE_IMP)
            else:
                self._parser.error('no database file found in current directory, use -f to specify')
        if not os.path.exists(self.work_path) and not os.path.isdir(self.work_path):
            os.mkdir(self.work_path)
        shutil.copyfile(self._database_file, os.path.join(self.work_path, 'workCopy.yml'))
        self.print_message('Creating work copy in: ' + str(os.path.join(self.work_path, 'workCopy.yml')), False)
        try:
            if self._database.load(os.path.realpath(os.path.join(self.work_path, 'workCopy.yml'))):
                self.print_message('Database workCopy.yml load OK', Cli.MESSAGE_IMP)

            if self._options.add_record:
                self.add()
            elif self._options.delete_id:
                self.delete()
            elif self._options.search_string:
                self.search()
            else:
                self.graph()
        except FormatError as ex:
            self.print_message('Database error:', Cli.MESSAGE_ERR)
            print(ex)


if __name__ == "__main__":
    data = 'data.yml'
    cli = Cli()
    cli.run()

#!/usr/bin/python3
import glob
import os
import shutil
import optparse
import re
import sys
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

        self._parser = optparse.OptionParser('Usage: ./Cli.py  -a | -g | -l | -d ID | -s STRING [-f FILE] \nExamples:\n'
                                             './Cli.py -a\n'
                                             './Cli.py -g\n'
                                             './Cli.py -d 42\n'
                                             './Cli.py -s bear\n'
                                             './Cli.py -s bear -f database.yml\n'
                                             './Cli.py -l')

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

        self._parser.add_option('-l', '--list', default=False,
                                action="store_true", dest="list_all",
                                help="List all records in database")

        self._parser.add_option('-s', '--search', type='string',
                                action="store", dest="search_string",
                                help="Search for this string in the database, if empty all records are printed")

        self._options, _ = self._parser.parse_args()
        option_combination = [self._options.add_record, self._options.delete_id,
                              self._options.make_graph, self._options.search_string, self._options.list_all]
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
                print('\t' + 'id: ' + Fore.LIGHTBLUE_EX + str(values['id']) + Fore.RESET)
                for attribute, content in values.items():
                    if attribute == 'id':
                        continue
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

    def _list_all(self) -> None:
        """
        List all records in the database.
        :return: None
        """
        self.print_message('List all records', Cli.MESSAGE_IMP)
        records = self._database.find('')
        self.print_record(records)
        self.print_message('\nDatabase contains: ' + str(len(records)) + ' records', Cli.MESSAGE_IMP)

    def _get_linkto(self, kind: bool) -> List[str]:
        """
        Return a list of linkto database records, ask the user to provide them.
        :param kind: True if link, False if email.
        :return: Return a list of linkto database records, ask the user to provide them.
        """
        link_list = []
        if kind:
            print('This account links to:')
        else:
            print('Associated e-mail addresses:')
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
    def _get_simple_attribute(name: str, empty: bool) -> str:
        """
        Ask the user for an attribute and return it.
        :param name: The name of the attribute to get
        :param empty: Can it be empty, True if it can?
        :return: str, the attribute from user.
        """
        attribute = ''
        while not attribute:
            attribute = str(input(name + ': ')).lstrip().rstrip()
            if empty:
                return attribute
        return attribute

    def _get_web_address(self) -> str:
        """
        Ask the user for a valid website address and return it.
        :return: Valid website address.
        """
        address = ''
        while not address.startswith('www.'):
            address = self._get_simple_attribute('Website address', False)
        return address

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
            password = self._get_simple_attribute('Password', False)
            question = self._get_simple_attribute('Security question', True)
            linktos = self._get_linkto(True)
            notes = self._get_simple_attribute('Additional notes', True)
            self.print_message('\nSaving new e-mail record', Cli.MESSAGE_IMP)
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
            self.print_message('\nAdding a new website', Cli.MESSAGE_IMP)
            web_name = self._get_web_address()
            login = self._get_simple_attribute('Login', False)
            password = self._get_simple_attribute('Password', False)
            question = self._get_simple_attribute('Security question', True)
            emails = self._get_linkto(False)
            linktos = self._get_linkto(True)
            notes = self._get_simple_attribute('Additional notes', True)
            self.print_message('\nSaving new website record', Cli.MESSAGE_IMP)
            # Record example
            # {'www.github.com': {'email': ['white@gmail.com'], 'id': 5, 'linkto': None, 'login': 'athwale',
            # 'notes': None, 'password': 'probablyisnt', 'question': 'dog'}}
            new_record = {web_name: {'email': (emails if emails else None), 'id': record_id,
                                     'linkto': (linktos if linktos else None), 'login': login,
                                     'notes': (notes if notes else None), 'password': password,
                                     'question': (question if question else None)}}
            if self._database.add('websites', new_record):
                self.print_message('Record added, database saved', Cli.MESSAGE_IMP)

        # Add a company
        if selection == 'c':
            self.print_message('\nAdding a new company', Cli.MESSAGE_IMP)
            company_name = self._get_simple_attribute('Company name', False)
            emails = self._get_linkto(False)
            linktos = self._get_linkto(True)
            notes = self._get_simple_attribute('Additional notes', True)
            self.print_message('\nSaving new company record', Cli.MESSAGE_IMP)
            # Record example
            # {'Zoo': {'email': [], 'id': 9, 'linkto': [], 'notes': None}}
            new_record = {company_name: {'email': (emails if emails else None), 'id': record_id,
                                         'linkto': (linktos if linktos else None),
                                         'notes': (notes if notes else None)}}
            if self._database.add('companies', new_record):
                self.print_message('Record added, database saved', Cli.MESSAGE_IMP)

        # Save to disk and replace
        if not self._replace_database():
            raise FormatError('Error replacing database')

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
                    raise FormatError('Error replacing database')
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
                self._parser.error('no database file found in current directory, use -f to specify '
                                   'or create an empty .yml file')
        if not os.path.exists(self.work_path) and not os.path.isdir(self.work_path):
            os.mkdir(self.work_path)
        try:
            if not os.path.exists(self._database_file):
                raise FormatError('Database file: ' + str(self._database_file) + ' does not exist')
            shutil.copyfile(self._database_file, os.path.join(self.work_path, 'workCopy.yml'))
            self.print_message('Creating work copy in: ' + str(os.path.join(self.work_path, 'workCopy.yml')), False)
            if self._database.load(os.path.realpath(os.path.join(self.work_path, 'workCopy.yml'))):
                self.print_message('Database workCopy.yml load OK', Cli.MESSAGE_IMP)
            else:
                self._parser.error('Incorrect database file')

            if self._options.add_record:
                self.add()
            elif self._options.delete_id:
                self.delete()
            elif self._options.search_string:
                self.search()
            elif self._options.list_all:
                self._list_all()
            else:
                self.graph()
        except FormatError as ex:
            self.print_message('Database error:', Cli.MESSAGE_ERR)
            print(ex, file=sys.stderr)


if __name__ == "__main__":
    data = 'data.yml'
    cli = Cli()
    cli.run()

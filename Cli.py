#!/usr/bin/python3
import glob
import os
import shutil
import optparse

from Database import Database
from colorama import Fore

from FormatError import FormatError


class Cli:

    def __init__(self):
        """
        Gui class constructor. Initialize database file name and database object.
        """
        self._database_file = None
        self._database = Database()

        self._parser = optparse.OptionParser('Usage: ./Cli.py  -a | -g | -d ID | -s STRING [-f FILE] \nExamples:\n'
                                             './Cli.py -a\n'
                                             './Cli.py -g\n'
                                             './Cli.py -d 42\n'
                                             './Cli.py -s bear\n'
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
    def print_message(message: str, err: bool) -> None:
        """
        Print a nice looking message on the screen.
        :param message:
        :param err: True if the message should be an error.
        :return: None
        """
        newline = ''
        # If the message begins with a new line add it before the ##
        if message[0] == '\n':
            newline = '\n'
            message = message[1:]
        if err:
            print(Fore.RED + newline + '## ' + str(message) + Fore.RESET)
        else:
            print(newline + '## ' + str(message))

    def search(self) -> None:
        """
        Run database search and print results.
        :return: None
        """
        self.print_message('Searching for: ' + self._options.search_string, False)
        records = self._database.find(self._options.search_string)
        self.print_record(records)
        self.print_message('\nFound: ' + str(len(records)) + ' database records', False)

    def add(self):
        """

        :return:
        """

    def delete(self):
        """

        :return:
        """

    def graph(self) -> None:
        """
        Create a graph of the database. Back up old version of the graph if exists in the directory.
        :return: None
        """
        self.print_message('Creating database graph', False)
        # Rename previous graph
        file_path = os.path.join('.', 'graph.pdf')
        if os.path.exists(file_path):
            self.print_message('Backing up previous graph', False)
            os.rename(file_path, os.path.join('.', 'graph.old.pdf'))
        self._database.graph('graph')
        # Remove intermediate file
        os.remove(os.path.join('.', 'graph'))
        self.print_message('Graph saved: ' + str(os.path.join('.', 'graph.pdf')), False)

    def run(self) -> None:
        """
        This method begins the user interaction with the database.
        :return: None
        """
        work_path = os.path.join('.', 'workDir')
        if self._options.database_file:
            self._database_file = self._options.database_file
        else:
            yml_files = glob.glob('*.yml')
            if yml_files:
                self._database_file = yml_files[0]
                self.print_message('Using database: ' + str(self._database_file), False)
            else:
                self._parser.error('no database file found in current directory, use -f to specify')
        if not os.path.exists(work_path) and not os.path.isdir(work_path):
            os.mkdir(work_path)
        shutil.copyfile(self._database_file, os.path.join(work_path, 'workCopy.yml'))
        self.print_message('Creating work copy in: ' + str(os.path.join(work_path, 'workCopy.yml')), False)
        try:
            if self._database.load(os.path.realpath(os.path.join(work_path, 'workCopy.yml'))):
                self.print_message('Database workCopy.yml load OK', False)

            if self._options.add_record:
                self.add()
            elif self._options.delete_id:
                self.delete()
            elif self._options.search_string:
                self.search()
            else:
                self.graph()
        except FormatError as ex:
            self.print_message('Database error:', True)
            print(ex)


if __name__ == "__main__":
    data = 'data.yml'
    cli = Cli()
    cli.run()


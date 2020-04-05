import yaml
from FormatError import FormatError


class Database:
    """

    """

    DATABASE_ERROR = 'Database format error, '

    def __init__(self, file: str):
        """
        Constructor for database communicator.
        :param file: str, database file name.
        """
        self._database_file = file
        self._validate()

    def _validate(self):
        """
        Check database file for errors.
        :return:
        """
        with open(self._database_file, "r") as yml:
            data = yaml.safe_load(yml)
            # Check main sections
            for section in ['emails', 'websites', 'companies']:
                if section not in data.keys():
                    raise FormatError(self.DATABASE_ERROR + str(section) + ' not in database.')

            # Check mail section
            for mail in data['emails']:
                if len(mail.keys()) > 1:
                    raise FormatError(self.DATABASE_ERROR + str(mail) + ' record is malformed')
                # Check mail format
                for address in mail.keys():
                    for char in ['@', '.']:
                        if char not in address:
                            raise FormatError(self.DATABASE_ERROR + str(address) + ' is missing "' + str(char) + '"')


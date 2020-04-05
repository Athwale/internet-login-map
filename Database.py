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
                for address, values in mail.items():
                    for char in ['@', '.']:
                        if char not in address:
                            raise FormatError(self.DATABASE_ERROR + str(address) + ' is missing "' + str(char) + '"')
                    # Check attribute names
                    self._attribute_check(['password', 'question', 'linkto', 'notes'], values)
                    # Check that linkto points to an existing record
                    if values['linkto']:
                        for link in values['linkto']:
                            self._linkto_check(data, link, address)

    def _linkto_check(self, data, node: str, source: str) -> None:
        """
        Check that node exists in the database. This is used to check that linkto and email point to an existing record
        in the database.
        :param data: Loaded yaml database.
        :param node: str, The name of the node we are checking for existence.
        :param source: str, The name of the node where the node was found.
        :return: None
        :exception FormatError if the node does not exist in the database.
        """
        for _, values in data.items():
            for record in values:
                if list(record)[0] == node:
                    return
        raise FormatError(self.DATABASE_ERROR + str(source) + ' points to invalid record ' + str(node))

    def _attribute_check(self, valid_list, attr_dict) -> None:
        """
        Check that keys in attr_dict only have names listed in valid_list.
        :param valid_list: List of allowed string key names (attributes in yaml)
        :param attr_dict: Record attributes from yaml. Like email data.
        :return: None
        :exception FormatError if attributes do not match.
        """
        for attr in attr_dict.keys():
            if attr not in valid_list:
                raise FormatError(self.DATABASE_ERROR + 'invalid attribute "' + str(attr) + '"')

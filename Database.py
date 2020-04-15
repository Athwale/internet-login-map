from typing import List

import yaml

from FormatError import FormatError


class Database:
    """
    This class works with the yaml database. Performs add, remove, change, find and validation.
    """

    DATABASE_FORMAT_ERROR = 'Database format error, '
    DATABASE_ERROR = 'Database error, '

    def __init__(self, file: str):
        """
        Constructor for database communicator.
        :param file: str, database file name.
        """
        self._database_file = file
        self._id_list = []

    def validate(self) -> bool:
        """
        Check database file for errors.
        :return: bool True if validation passed, exception FormatError is thrown otherwise.
        """
        self._id_list.clear()
        with open(self._database_file, "r") as yml:
            data = yaml.safe_load(yml)
            # Check main sections
            for section in ['emails', 'websites', 'companies']:
                if section not in data.keys():
                    raise FormatError(self.DATABASE_FORMAT_ERROR + str(section) + ' not in database.')

            # Check mail section
            # Check that each email has an id. Check that each email has @ and . in it. Check that each email record has
            # required attributes. Check that email password is not empty. Check that each linkto attribute points to
            # existing record.
            for mail in data['emails']:
                if len(mail.keys()) > 1:
                    raise FormatError(self.DATABASE_FORMAT_ERROR + str(mail) + ' record is malformed')
                for address, values in mail.items():
                    # Check id
                    self._id_check(values, address)
                    # Check mail format
                    for char in ['@', '.']:
                        if char not in address:
                            raise FormatError(self.DATABASE_FORMAT_ERROR + str(address) + ' is missing "' + str(char)
                                              + '"')
                    # Check attribute names
                    self._attribute_check(['id', 'login', 'password', 'question', 'linkto', 'notes'], values, address)
                    # Check password is not empty
                    if not values['password']:
                        raise FormatError(self.DATABASE_FORMAT_ERROR + str(address) + ' has empty password')
                    # Check that linkto points to an existing record
                    if values['linkto']:
                        self._linkto_check(data, values['linkto'], address)

            # Check website section
            # Check that website begins with www and contains a dot. Check that each website record has required
            # attributes. Check that password/login is not empty. Check that each linkto/email attribute points
            # to an existing record. Check correct id.
            for website in data['websites']:
                if len(website.keys()) > 1:
                    raise FormatError(self.DATABASE_FORMAT_ERROR + str(website) + ' record is malformed')
                # Check website format
                for web_address, values in website.items():
                    # Check id
                    self._id_check(values, web_address)
                    if 'www.' not in web_address:
                        raise FormatError(self.DATABASE_FORMAT_ERROR + str(web_address) + ' is missing www.')
                    if len(web_address.split('.')) < 3:
                        raise FormatError(self.DATABASE_FORMAT_ERROR + str(web_address) + ' is malformed')
                    # Check attribute names
                    self._attribute_check(['id', 'login', 'password', 'email', 'question', 'linkto', 'notes'],
                                          values, web_address)
                    # Check password and login is not empty
                    if not values['login']:
                        raise FormatError(self.DATABASE_FORMAT_ERROR + str(web_address) + ' has empty login')
                    if not values['password']:
                        raise FormatError(self.DATABASE_FORMAT_ERROR + str(web_address) + ' has empty password')
                    # Check that emails point to an existing record
                    if values['email']:
                        self._linkto_check(data, values['email'], web_address)
                    # Check that each linkto point to an existing record
                    if values['linkto']:
                        self._linkto_check(data, values['linkto'], web_address)

            # Check company section
            # Check that each company record has required attributes. Check that each linkto/email attribute points to
            # an existing record. Check correct id.
            for company in data['companies']:
                if len(company.keys()) > 1:
                    raise FormatError(self.DATABASE_FORMAT_ERROR + str(company) + ' record is malformed')
                for company_name, values in company.items():
                    # Check id
                    self._id_check(values, company_name)
                    # Check attribute names
                    self._attribute_check(['id', 'email', 'linkto', 'notes'], values, company_name)
                    # Check that emails point to an existing record
                    if values['email']:
                        self._linkto_check(data, values['email'], web_address)
                    # Check that each linkto point to an existing record
                    if values['linkto']:
                        self._linkto_check(data, values['linkto'], web_address)
        return True

    def _id_check(self, values, source: str) -> None:
        """
        Check that id is valid and has never been used anywhere else.
        :param values: a dictionary of values of a record
        :param source: the name of the record
        :return: None
        """
        record_id = values['id']
        if record_id:
            if not isinstance(record_id, int):
                raise FormatError(self.DATABASE_FORMAT_ERROR + str(source) + ' has non-integer id: ' + str(record_id))
            if not record_id > 0:
                raise FormatError(self.DATABASE_FORMAT_ERROR + str(source) + ' has incorrect id: ' + str(record_id))
        else:
            if record_id == 0:
                raise FormatError(self.DATABASE_FORMAT_ERROR + str(source) + ' id must be positive')
            raise FormatError(self.DATABASE_FORMAT_ERROR + str(source) + ' has no id')
        # Check for duplicity
        if record_id in self._id_list:
            raise FormatError(self.DATABASE_FORMAT_ERROR + str(source) + ' has duplicate id: ' + str(record_id))
        else:
            self._id_list.append(record_id)

    def _linkto_check(self, data, links: List[str], source: str) -> None:
        """
        Check that node exists in the database. This is used to check that linkto and email point to an existing record
        in the database. Also check that links and emails are not duplicated.
        :param data: Loaded yaml database.
        :param links: List of str links/emails of the given website or company or email
        :param source: str, The name of the node where the node was found.
        :return: None
        :exception FormatError if the node does not exist in the database.
        """
        records = []
        # Get all top level nodes
        for _, values in data.items():
            for record in values:
                # Get each record name into a common list of all records
                records.append(list(record)[0])
        for link in links:
            if link not in records:
                raise FormatError(self.DATABASE_FORMAT_ERROR + str(source) + ' points to invalid record ' + str(link))
            if links.count(link) > 1:
                raise FormatError(self.DATABASE_FORMAT_ERROR + str(source) + ' contains duplicates of ' + str(link))

    def _attribute_check(self, valid_list: List[str], attr_dict, source: str) -> None:
        """
        Check that keys in attr_dict only have names listed in valid_list.
        :param valid_list: List of allowed string key names (attributes in yaml)
        :param attr_dict: Record attributes from yaml. Like email data.
        :param source: str, The name of the node where the node was found.
        :return: None
        :exception FormatError if attributes do not match.
        """
        # Check each attribute is in the list once
        for attr in valid_list:
            if attr not in list(attr_dict):
                raise FormatError(self.DATABASE_FORMAT_ERROR + str(source) + ' missing or typo in attribute "' +
                                  str(attr) + '"')
        if sorted(list(attr_dict)) != sorted(valid_list):
            extra = set(attr_dict).difference(set(valid_list))
            raise FormatError(self.DATABASE_FORMAT_ERROR + str(source) + ' has extra attribute/s: ' + str(extra))

    @staticmethod
    def _add_in_not_in(item, dict_list):
        """
        Add item to list only if it is not already in there.
        :param item: Item to add, this is a dictionary yaml database record with one key.
        :param dict_list: This is a list of of items as above.
        :return: None
        """
        item_key = list(item)[0]
        found_keys = [list(name)[0] for name in dict_list]
        if item_key not in found_keys:
            dict_list.append(item)

    def find(self, string: str):
        """
        Find records in database that contain the string. Go through all records and look for the string.
        :param string: The strings that the record must contain.
        :return: A list of yaml records.
        """
        found = []
        string = string.lower()
        with open(self._database_file, "r") as yml:
            data = yaml.safe_load(yml)
            # Check main sections
            for section in ['emails', 'websites', 'companies']:
                for record in data[section]:
                    # Special case empty search string means we want all
                    if not string:
                        self._add_in_not_in(record, found)
                    else:
                        # Check node names
                        if string in list(record)[0].lower():
                            self._add_in_not_in(record, found)
                        # Check inner data
                        data_dict = record[list(record)[0]]
                        for attribute, content in data_dict.items():
                            if isinstance(content, List):
                                for item in content:
                                    if item and string in str(item):
                                        self._add_in_not_in(record, found)
                            else:
                                if content and string in str(content):
                                    self._add_in_not_in(record, found)
        if not found:
            raise FormatError(self.DATABASE_ERROR + 'nothing found')
        return found

    def add(self) -> bool:
        """

        :return: True if added successfully.
        """
        with open(self._database_file, "r") as yml:
            data = yaml.safe_load(yml)
            self.save(data)
            return True

    def delete(self, record_id: int) -> bool:
        """
        Remove a record from the database based on the record ID. Then save the new database onto disk rewriting the
        current workCopy file.
        :param record_id: int id of the record to be deleted
        :return: True if removed successfully.
        """
        with open(self._database_file, "r") as yml:
            data = yaml.safe_load(yml)
            # Go through everything looking for the id
            for section in ['emails', 'websites', 'companies']:
                for record in data[section]:
                    data_dict = record[list(record)[0]]
                    if data_dict['id'] == record_id:
                        del data[section][data[section].index(record)]
                        return self.save(data)
            raise FormatError(self.DATABASE_ERROR + 'record: ' + str(record_id) + ' not found')

    def save(self, yml) -> bool:
        """
        Save database onto disk replacing the workCopy file on disk.
        :param yml: Modified yaml database to save.
        :return: True if saved successfully.
        """
        with open(self._database_file, 'w') as output_file:
            yaml.safe_dump(yml, output_file)
        return True

""" AWS Accounts class. """
import boto3
from boto3.dynamodb.conditions import Key, Attr


class AwsAccounts(object):
    """ AWS Accounts class """

    m_dynamo = None
    """ :type: pyboto3.dynamodb """

    def __init__(self, session=None):
        """ When used on a thread, constructor requires a session
        When using AwsAccounts with threads, each thread must use its own
        session and not use default session.  As a result, AwsAccount
        requires the user to pass in the session the accounts class will be
        used on, on construction.  If none is passed in, the default will
        be used, which is not thread safe.

        :param session: Session created on current thread, or none
        """
        if session:
            self.m_table = session.resource('dynamodb').Table(
                'AWS-Accounts-Table')
        else:
            self.m_table = boto3.resource('dynamodb').Table(
                'AWS-Accounts-Table')

    def with_number(self, account_number):
        """ Find the account that matches the account_number

        :param account_number: Account number to match
        :return: Dictionary for account with number or None
        """
        result = self.m_table.query(
            KeyConditionExpression=Key('accountNum').eq(str(account_number)))
        accounts = result['Items']

        if accounts:
            return accounts[0]

        return None

    def with_alias(self, alias):
        """ Find the account with a given alias

        :param alias: Account alias to match
        :return: Dictionary for account with number or None
        """
        scan = self.m_table.scan(
            Select='ALL_ATTRIBUTES',
            FilterExpression=Attr('alias').eq(alias))
        accounts = scan['Items']
        if scan['Count'] == 0:  # Always happens when filter works
            return None
        elif scan['Count'] == 1:
            return accounts[0]
        else:
            # This only happens in moto, which doesn't handle filter correctly
            # So, here we filter ourselves
            for cur in accounts:
                if cur['alias'] == alias:
                    return cur
        return None

    def all(self, attr=None):
        """ Find the account with a given alias

        :param attr: list of attributes to get
        :return: Dictionary for account with number or None
        """
        if not attr:
            scan = self.m_table.scan(Select='ALL_ATTRIBUTES')
        else:
            scan = self.m_table.scan(
                Select='SPECIFIC_ATTRIBUTES', AttributesToGet=attr)
        return scan['Items']

    def count(self):
        """ Returns the number of elements in the Table
        """
        accounts = self.m_table.scan(
            Select='COUNT')
        return accounts['Count']

    def add(self, attr):
        """ Add an account with given attributes
        :param attr: list of attributes to add (accountNum is required)
        :return bool
        """
        if attr:
            resp = self.m_table.put_item(
                Item={
                    'accountNum': str(attr.get('accountNum')),
                    'alias': str(attr.get('alias')),
                    'email': str(attr.get('email')),
                    'AccountOwner': str(attr.get('owner'))
                }
            )
            if resp:
                return True
        return False

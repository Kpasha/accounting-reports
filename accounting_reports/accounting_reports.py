'''
Accounting Reports

Usage:
  accounting-reports chart-of-accounts --db=<PATH>
  accounting-reports balances --db=<PATH> [--accounts=<ACCOUNTS>] [--begin=<BEGIN_DATE>] [--end=<END_DATE>] [--output=<FORMAT>] [--verbose]
  accounting-reports -h | --help
  accounting-reports --version
  accounting-reports --verbose
Options:
  --db=<PATH>           Path to SQLite file.
  --accounts=<ACCOUNTS> Comma separated list of accounts to get balances for. Default: all.
  --begin=<BEGIN_DATE>  Begin date of balances (yyyy-mm-dd).  Default: first day of the year.
  --end=<END_DATE>      Date to get balances as-of (yyyy-mm-dd).  Default: last day of previous month.
  --output=<FORMAT>     Format to output results in (csv, json). [Default: csv]
  --verbose             Verbose logging.
  -h --help             Show this screen.
  --version             Show version.
'''

from .version import __version__
from .util import configure_logging, csv_to_list, filter_list, begin_or_default, end_or_default, output_arg
from logging import info, debug
from docopt import docopt
from piecash import open_book


def account_balances(db, accounts, begin, end, output_func):
  debug('account_balance called with [%s] [%s] [%s--%s]' % (db, accounts, begin, end))
  balances = []
  with open_book(db) as book:
    acctlist = filter_list(book.accounts, accounts)
    for account in acctlist:
        output_func(account, balance_of(account, begin, end))


def balance_of(account, begin, end):
  debug('balance_of account:[%s] over[%s--%s]' % (account, begin, end))
  if end:
      balance=0
      for split in account.splits:
        transaction = split.transaction
        post_date = transaction.post_date.date()
        if post_date >= begin and post_date < end:
          debug('post_date (%s) is between (%s--%s)' % (transaction.post_date.date(), begin, end))
          balance += split.value * account.sign
      return balance
  else:
      return account.get_balance()


def chart_of_accounts(db):
  with open_book(db) as book:
      for acc in book.accounts:
          if(acc.code):
            print('%d\t%s\t%s' % (int(acc.code), acc.type, acc.fullname))


def main():
  args = docopt(__doc__, version=__version__)
  configure_logging(args['--verbose'])

  db_file = args['--db']
  accounts = csv_to_list(args['--accounts'])
  begin = begin_or_default(args['--begin'])
  end = end_or_default(args['--end'])

  output_func=output_arg(args['--output'])

  if(args['chart-of-accounts']):
    chart_of_accounts(db_file)

  if(args['balances']):
    account_balances(db_file, accounts, begin, end, output_func)

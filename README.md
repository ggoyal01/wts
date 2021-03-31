# WalletTransactionSystem

This is a basic Wallet Transaction System. You can create wallet for a user (identified by phone number) and do transactions on it.

Instructions for running server:
1. Clone the repo. Cd to the repo.
2. Create virtual env -> `python3 -m venv venv`
3. Install the dependencies -> `pip install -r requirements.txt`
4. Run the server -> `flask run`
5. Test using Postman. (Import the 'swagger.yaml' file to get the collection of APIs)


phnone - Phone numbers valid in India. As every country has different pattern chose 1 country to validate data.

amount - Can be a string or a float.

Log in to sqlite db from terminal to see `transaction log`.
1. sqlite wts.db (need to install sqlite first)
2. .tables -> to show tables
3. .schema <table_name> -> to get schema of a particular table


MIN_BAL(default - 500.00) and DATABASE path(default - project directory) are maintained in `.flaskenv` file.
Can be edited according to the requirement.

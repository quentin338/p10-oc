# Purbeurre-p8
-
*Python 3.7+*  
*Output French products*

## How to use
- Clone the repository
- Install your venv
- pip install -r requirements.txt
- Install/Config a PostgreSQL DB
- Create a .env with the differents variables (see settings.py)
#### Install DB
- python manage.py migrate
#### Populate DB
- python manage.py db_init -c XX -p YY  
*-c* for the number of categories  
*-p* for the number of products by category


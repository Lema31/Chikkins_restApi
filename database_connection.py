import psycopg2

try:
 connection = psycopg2.connect(
     host = 'localhost',
     user =  'lema',
     password = '7WPtab0HU6CO$0G',
     database = 'chikkinsRestaurant',
     port = 5432
 )
except Exception as ex:
    print(ex)
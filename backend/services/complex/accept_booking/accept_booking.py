# accept booking. click link, login, retrieve user_id, phone num, username from user session variable.
# pull them from user DB

# order_id, price, payment ID pull from order db (get order details based on userID)

# separate UI with form auto filled up with those details (order details, restaurant name) 

# TO FILL UP
# count, table num

# then once user confirm, call create reservation in create reservation from reservation.py

#success 200, queue msg to rabbitmq

# queue username, ph num, table no, 
# "reallocation.confirmation": "Table {table_no} booking has been confirmed. Thank you!"
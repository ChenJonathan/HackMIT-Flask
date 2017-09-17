import pymysql, random
from datetime import date
from dateutil.relativedelta import relativedelta
from config import DevelopmentConfig as myConfig

db = pymysql.connect(myConfig.MYSQL_DATABASE_HOST, myConfig.MYSQL_DATABASE_USER,
    myConfig.MYSQL_DATABASE_PASSWORD, myConfig.MYSQL_DATABASE_DB)
cursor = db.cursor()

num_users = 1000
cities = []
for line in open("cities.csv", "r"):
  city, visitors = line.split(",")
  cities.append([city, visitors])
print(cities)

# Generate num_users amount of new users
for i in range(num_users):
  # Calculate this user's user_id
  # cursor.execute("SELECT COUNT(*) FROM `users`")
  # user_id = cursor.fetchone()[0] + 1
  user_id = 0
  print("%d/%d" % (user_id, num_users))

  user_loc = random.randint(0, len(cities) - 1)

  # Insert the user into the database
  # cursor.execute("INSERT INTO `users`(`email`,`password`,`location`) VALUES (%s,%s,%s)",
    # ["user_%d@email.com" % user_id, "user_%d" % user_id, cities[user_loc][0]])
  # db.commit()

  # cursor.execute("SELECT `user_id` FROM `users` WHERE `email`=%s",
    # ["user_%d@email.com" % user_id])
  # user_id = cursor.fetchone()[0]

  # Generate [1, 20] trips for this user
  num_trips = random.randint(1, 10)
  print("num_trips: %d" % num_trips)
  for trip in range(num_trips):
    print("%d/%d" % (trip, num_trips))

    trip_loc = random.randint(0, len(cities) - 1)
    while trip_loc == user_loc:
      trip_loc = random.randint(0, len(cities) - 1)

    start_range = (date.today() - relativedelta(years=2)).toordinal()
    end_range = date.today().toordinal()
    day1 = date.fromordinal(random.randint(start_range, end_range))
    day2 = date.fromordinal(random.randint(start_range, end_range))
    start_date = day1 if day1 < day2 else day2
    end_date = day2 if day1 < day2 else day1

    duration = random.randint(2, 14)

    print("(%s,%s,%s,%s,%s)" % (user_id, cities[trip_loc][0], start_date,
      end_date, duration))

    # cursor.execute("INSERT INTO `bucket_items`(`user_id`,`end_city`,"
      # "`start_date`,`end_date`,`duration`) VALUES (%s,%s,%s,%s,%s)", [user_id,
      # cities[trip_loc], start_date, end_date, duration])
    # db.commit()
# db.close()
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Pass1243@restaurant-db.cno4eciqml61.us-east-1.rds.amazonaws.com/restaurantdb")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")

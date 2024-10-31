from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel
import pymysql
from hashlib import sha256
from schemas import UserCreate, User, UserUpdate, BucketListItemCreate, BucketListItem, BucketListUpdate, ReminderCreate, Reminder, BudgetCreate, BudgetUpdate, Budget
 # Assuming schemas are defined in schemas.py

app = FastAPI()

def get_db_connection():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',      
            password='',      
            database='bucketlist_db', 
            cursorclass=pymysql.cursors.DictCursor
        )
        print("Database connection successful")
        return connection
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        raise e

# Create user
@app.post("/users/")
def create_user(user: UserCreate):
    connection = get_db_connection()
    cursor = connection.cursor()
    hashed_password = sha256(user.password.encode()).hexdigest()
    sql = "INSERT INTO users (username, email, hashed_password) VALUES (%s, %s, %s)"
    cursor.execute(sql, (user.username, user.email, hashed_password))
    connection.commit()
    user_id = cursor.lastrowid
    cursor.close()
    connection.close()
    return {"status": "User created successfully", "user_id": user_id}

# Get user by ID
@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    sql = "SELECT id, username, email FROM users WHERE id = %s"
    cursor.execute(sql, (user_id,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return User(**result)

# Update user by ID
@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user_update: UserCreate):
    connection = get_db_connection()
    cursor = connection.cursor()
    hashed_password = sha256(user_update.password.encode()).hexdigest()
    sql = "UPDATE users SET username = %s, email = %s, hashed_password = %s WHERE id = %s"
    cursor.execute(sql, (user_update.username, user_update.email, hashed_password, user_id))
    connection.commit()
    cursor.close()
    connection.close()
    return User(id=user_id, username=user_update.username, email=user_update.email)

# Delete user by ID
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    sql = "DELETE FROM users WHERE id = %s"
    cursor.execute(sql, (user_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return {"status": "User deleted successfully"}




# Create bucket list item
@app.post("/bucketlist/")
def create_bucket_list_item(item: BucketListItemCreate):
    connection = get_db_connection()
    cursor = connection.cursor()
    sql = "INSERT INTO bucketlist (title, description) VALUES (%s, %s)"
    cursor.execute(sql, (item.title, item.description))
    connection.commit()
    item_id = cursor.lastrowid
    cursor.close()
    connection.close()
    return {"status": "Bucket list item created successfully", "item_id": item_id}

# Get bucket list item by ID
@app.get("/bucketlist/{item_id}", response_model=BucketListItem)
def get_bucket_list_item(item_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    sql = "SELECT id, title, description FROM bucketlist WHERE id = %s"
    cursor.execute(sql, (item_id,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return BucketListItem(**result)

# Update bucket list item by ID
@app.put("/bucketlist/{item_id}", response_model=BucketListItem)
def update_bucket_list_item(item_id: int, item_update: BucketListItemCreate):
    connection = get_db_connection()
    cursor = connection.cursor()
    sql = "UPDATE bucketlist SET title = %s, description = %s WHERE id = %s"
    cursor.execute(sql, (item_update.title, item_update.description, item_id))
    connection.commit()
    cursor.close()
    connection.close()
    return BucketListItem(id=item_id, title=item_update.title, description=item_update.description)

# Delete bucket list item by ID
@app.delete("/bucketlist/{item_id}")
def delete_bucket_list_item(item_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    sql = "DELETE FROM bucketlist WHERE id = %s"
    cursor.execute(sql, (item_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return {"status": "Bucket list item deleted successfully"}

# Mark Bucket List Item as Completed
@app.put("/bucketlist/{item_id}/complete", response_model=BucketListItem)
def mark_completed(item_id: int, completed: bool):
    connection = get_db_connection()
    cursor = connection.cursor()
    sql = "UPDATE bucketlist SET completed = %s WHERE id = %s"
    cursor.execute(sql, (completed, item_id))
    connection.commit()
    cursor.close()
    connection.close()
    return {"status": "Bucket list item updated successfully", "completed": completed}



#reminers
@app.post("/reminders/", response_model=Reminder)
def create_reminder(reminder: ReminderCreate):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        sql = "INSERT INTO reminders (user_id, bucketlist_item_id, reminder_date, message) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (reminder.user_id, reminder.bucketlist_item_id, reminder.reminder_date, reminder.message))
        connection.commit()
        reminder_id = cursor.lastrowid
        
        return {**reminder.dict(), "id": reminder_id}
        
    except Exception as e:
        connection.rollback()  # Roll back if an error occurs
        print(f"Error occurred while creating reminder: {e}")  # Log the error
        raise HTTPException(status_code=500, detail="Could not create reminder")
        
    finally:
        cursor.close()
        connection.close()

@app.get("/reminders/{reminder_id}", response_model=Reminder)
def get_reminder(reminder_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    sql = "SELECT id, bucketlist_item_id, reminder_date, message FROM reminders WHERE id = %s"
    cursor.execute(sql, (reminder_id,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return Reminder(**result)

@app.put("/reminders/{reminder_id}", response_model=Reminder)
def update_reminder(reminder_id: int, reminder_update: ReminderCreate):
    connection = get_db_connection()
    cursor = connection.cursor()
    sql = "UPDATE reminders SET bucketlist_item_id = %s, reminder_date = %s, message = %s WHERE id = %s"
    cursor.execute(sql, (reminder_update.bucketlist_item_id, reminder_update.reminder_date, reminder_update.message, reminder_id))
    connection.commit()
    cursor.close()
    connection.close()
    return {**reminder_update.dict(), "id": reminder_id}

@app.delete("/reminders/{reminder_id}")
def delete_reminder(reminder_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    sql = "DELETE FROM reminders WHERE id = %s"
    cursor.execute(sql, (reminder_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return {"status": "Reminder deleted successfully"}


#budget
# Create budget
@app.post("/budgets/", response_model=Budget)
def create_budget(budget: BudgetCreate):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        sql = """
        INSERT INTO budgets (user_id, bucketlist_item_id, budget_amount) 
        VALUES (%s, %s, %s)
        """
        cursor.execute(sql, (budget.user_id, budget.bucketlist_item_id, budget.budget_amount))
        connection.commit()
        budget_id = cursor.lastrowid
        cursor.close()
        connection.close()

        return {**budget.dict(), "id": budget_id}

    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating budget: {str(e)}")

# Get budget by ID
@app.get("/budgets/{budget_id}", response_model=Budget)
def get_budget(budget_id: int):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        sql = """
        SELECT id, bucketlist_item_id, budget_amount, spent_amount 
        FROM budgets WHERE id = %s
        """
        cursor.execute(sql, (budget_id,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Budget not found")
        cursor.close()
        connection.close()

        return Budget(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving budget: {str(e)}")

# Update budget by ID
@app.put("/budgets/{budget_id}", response_model=Budget)
def update_budget(budget_id: int, budget_update: BudgetUpdate):  #
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        sql = """
        UPDATE budgets 
        SET budget_amount = %s, spent_amount = %s 
        WHERE id = %s
        """
        cursor.execute(sql, (budget_update.budget_amount, budget_update.spent_amount, budget_id))
        connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Budget not found")
        cursor.close()
        connection.close()
        return {**budget_update.dict(), "id": budget_id}
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating budget: {str(e)}")

# Delete budget by ID
@app.delete("/budgets/{budget_id}")
def delete_budget(budget_id: int):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        sql = "DELETE FROM budgets WHERE id = %s"
        cursor.execute(sql, (budget_id,))
        connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Budget not found")
        cursor.close()
        connection.close()

        return {"status": "Budget deleted successfully"}

    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting budget: {str(e)}")
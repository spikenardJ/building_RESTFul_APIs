# Task 1: Setting Up the Flask Environment and Database Connection

from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
import mysql.connector
from mysql.connector import Error
from marshmallow import Schema, fields, ValidationError

app = Flask(__name__)
ma = Marshmallow(app)
my_password = "!Jaedyn77"

def get_db_connection():
    # Database connection parameters
    db_name = "fitness_center_db"
    user = "root"
    password = my_password
    host = "localhost"
    try:
        # Attempting to establish a connection
        conn = mysql.connector.connect(
            database=db_name,
            user=user,
            password=password,
            host=host
        )
        # Check if connection is successful
        print("Connected to MySQL database successfully.")
        return conn
    except Error as e:
        # Handling any connection errors
        print(f"Error: {e}")
        return None

# Task 2: Implementing CRUD Operations for Members

class MemberSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    age = fields.Int(required=True)
    phone = fields.Str(required=True)
    email = fields.Str(required=True)

class WorkoutSessionSchema(ma.Schema):
    session_id = fields.Int(dump_only=True)
    session_date = fields.Date(required=True)
    session_time = fields.Str(required=True)
    activity = fields.Str(required=True)
    member_id = fields.Int(required=True)

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)
workout_session_schema = WorkoutSessionSchema()
workout_sessions_schema = WorkoutSessionSchema(many=True)

# 4 routes. Add a Member, Retrieve a Member, Update a Member, Delete a Member
@app.route("/members", methods=["POST"])
def add_member():
    try:
        member = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"ERROR": "Database connection failed."}), 500
    
    try:
        cursor = conn.cursor()
        query = "INSERT INTO Members (name, age, phone, email) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (member["name"], member["age"], member["phone"], member["email"]))
        conn.commit()
        return jsonify({"MESSAGE": "Member added successfully."}), 201
    except Error as e:
        return jsonify({"ERROR": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/members/<int:id>", methods=["GET"])
def get_member(id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"ERROR": "Database connection failed."}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Members WHERE id = %s", (id,))
    member = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if member:
        return member_schema.jsonify(member)
    else:
        return jsonify({"ERROR": "Member not found."}), 404

@app.route("/members/<int:id>", methods=["PUT"])
def update_member(id):
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"ERROR": "Database connection failed."}), 500
    
    try:
        cursor = conn.cursor()
        query = "UPDATE Members SET name = %s, age = %s, phone = %s, email = %s WHERE id = %s"
        cursor.execute(query, (member_data["name"], member_data["age"], member_data["phone"], member_data["email"], id))
        conn.commit()
        return jsonify({"MESSAGE": "Member updated successfully."}), 200
    except Error as e:
        return jsonify({"ERROR": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/members/<int:id>", methods=["DELETE"])
def delete_member(id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"ERROR": "Database connection failed."}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Members WHERE id = %s", (id,))
        conn.commit()
        return jsonify({"MESSAGE": "Member deleted successfully."}), 200
    except Error as e:
        return jsonify({"ERROR": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Task 3: Managing Workout Sessions

@app.route("/members/<int:id>/add_workout_sessions", methods=["POST"])
def add_workout_session(id):
    try:
        workout_session = workout_session_schema.load(request.json)
        workout_session["member_id"] = id  # Associate the session with the member ID
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"ERROR": "Database connection failed."}), 500
    
    try:
        cursor = conn.cursor()
        query = "INSERT INTO WorkoutSessions (session_date, session_time, activity, member_id) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (workout_session["session_date"], workout_session["session_time"], workout_session["activity"], workout_session["member_id"]))
        conn.commit()
        return jsonify({"MESSAGE": "Workout session added successfully."}), 201
    except Error as e:
        return jsonify({"ERROR": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/members/<int:id>/update_workout_sessions/<int:session_id>", methods=["PUT"])
def update_workout_session(id, session_id):
    try:
        workout_session = workout_session_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"ERROR": "Database connection failed."}), 500
    
    try:
        cursor = conn.cursor()
        query = "UPDATE WorkoutSessions SET session_date = %s, session_time = %s, activity = %s WHERE session_id = %s AND member_id = %s"
        cursor.execute(query, (workout_session["session_date"], workout_session["session_time"], workout_session["activity"], session_id, id))
        conn.commit()
        return jsonify({"MESSAGE": "Workout session updated successfully."}), 200
    except Error as e:
        return jsonify({"ERROR": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/members/<int:id>/view_workout_sessions", methods=["GET"])
def view_member_workout_sessions(id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"ERROR": "Database connection failed."}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM WorkoutSessions WHERE member_id = %s", (id,))
    workout_sessions = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if workout_sessions:
        return workout_sessions_schema.jsonify(workout_sessions)
    else:
        return jsonify({"MESSAGE": "No workout sessions found for this member."}), 404

if __name__ == "__main__":
    app.run(debug=True)
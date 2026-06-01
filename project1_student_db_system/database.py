import mysql.connector
from Student import Student

class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="student_db"
        )
        self.cursor = self.conn.cursor()
    
    def insert_student(self, name, age, grade):
        query = "INSERT INTO students (name, age, grade) VALUES (%s, %s, %s)"
        self.cursor.execute(query, (name, age, grade))
        self.conn.commit()
    
    def insert_students_bulk(self, students_list):
        """
        Insert multiple students at once
        students_list: list of tuples [(name, age, grade), ...]
        """
        query = "INSERT INTO students (name, age, grade) VALUES (%s, %s, %s)"
        self.cursor.executemany(query, students_list)
        self.conn.commit()
    
    def fetch_data(self):
        self.cursor.execute("SELECT * FROM students")
        results = self.cursor.fetchall()
        students = []
        for row in results:
            students.append(Student(row[0], row[1], row[2], row[3]))
        return students
    
    def update_student(self, student_id, name, age, grade):
        query = "UPDATE students SET name=%s, age=%s, grade=%s WHERE id=%s"
        self.cursor.execute(query, (name, age, grade, student_id))
        self.conn.commit()
    
    def delete_student(self, student_id):
        query = "DELETE FROM students WHERE id=%s"
        self.cursor.execute(query, (student_id,))
        self.conn.commit()
    
    def close(self):
        self.cursor.close()
        self.conn.close()
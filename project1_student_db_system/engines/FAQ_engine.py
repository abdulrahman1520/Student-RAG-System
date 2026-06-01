from .base import ChatEngine

class StudentSQLEngine(ChatEngine):
    def __init__(self, database):
        self.db = database

    def answer(self, query: str) -> str:
        query = query.strip().lower()
        
        if query == "how many students?":
            students = self.db.fetch_data()
            return f"Total students: {len(students)}"
        
        elif query == "who is the oldest student?":
            students = self.db.fetch_data()
            if students:
                oldest = max(students, key=lambda s: s.age)
                return f"Oldest student: {oldest.name} - Age: {oldest.age}"
            return "No students found"
            
        elif query == "who is the youngest student?":
            students = self.db.fetch_data()
            if students:
                youngest = min(students, key=lambda s: s.age)
                return f"Youngest student: {youngest.name} - Age: {youngest.age}"
            return "No students found"
            
        elif query == "show all students":
            students = self.db.fetch_data()
            if students:
                result = "Students list:\n"
                for student in students:
                    result += f"- {student.name} (Age: {student.age}, Grade: {student.grade})\n"
                return result
            return "No students found"
            
        elif query == "what is the average age?":
            students = self.db.fetch_data()
            if students:
                avg_age = sum(s.age for s in students) / len(students)
                return f"Average age: {avg_age:.1f} years"
            return "No students found"
        
        else:
            return "I can only answer database questions. Switch to RAG mode for general queries."
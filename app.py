from flask import Flask, request, jsonify, render_template
import sqlite3, os

app = Flask(__name__)
DB = os.path.join(os.path.dirname(__file__), "university.db")

def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    return c

def rows(cursor): return [dict(r) for r in cursor.fetchall()]

def init_db():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS department (
            department_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            department_name TEXT    NOT NULL UNIQUE,
            location        TEXT    NOT NULL
        );
        CREATE TABLE IF NOT EXISTS designation (
            designation_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            designation_name TEXT    NOT NULL UNIQUE,
            base_salary      REAL    NOT NULL
        );
        CREATE TABLE IF NOT EXISTS pincode (
            pincode TEXT PRIMARY KEY,
            city    TEXT NOT NULL,
            state   TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS student (
            student_id    TEXT PRIMARY KEY,
            first_name    TEXT NOT NULL,
            last_name     TEXT NOT NULL,
            dob           TEXT,
            email         TEXT UNIQUE,
            phone         TEXT,
            street        TEXT,
            pincode       TEXT REFERENCES pincode(pincode),
            year_of_study INTEGER,
            department_id INTEGER REFERENCES department(department_id)
        );
        CREATE TABLE IF NOT EXISTS instructor (
            instructor_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            name           TEXT NOT NULL,
            email          TEXT UNIQUE,
            phone          TEXT,
            designation_id INTEGER REFERENCES designation(designation_id)
       );
        CREATE TABLE IF NOT EXISTS course (
            course_id     TEXT PRIMARY KEY,
            course_name   TEXT NOT NULL,
            credits       INTEGER,
            semester      TEXT,
            department_id INTEGER REFERENCES department(department_id)
        );
        CREATE TABLE IF NOT EXISTS course_instructor (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id     TEXT    REFERENCES course(course_id),
            instructor_id INTEGER REFERENCES instructor(instructor_id),
            UNIQUE(course_id, instructor_id)
        );
        CREATE TABLE IF NOT EXISTS course_textbook (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id TEXT REFERENCES course(course_id),
            textbook  TEXT NOT NULL,
            UNIQUE(course_id, textbook)
        );
        CREATE TABLE IF NOT EXISTS enrollment (
            enrollment_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id      TEXT    REFERENCES student(student_id),
            course_id       TEXT    REFERENCES course(course_id),
            grade           TEXT,
            enrollment_date TEXT
        );
        INSERT OR IGNORE INTO designation(designation_name, base_salary) VALUES
            ('Professor', 120000), ('Associate Professor', 95000),
            ('Assistant Professor', 75000), ('Lecturer', 55000);
        INSERT OR IGNORE INTO department(department_name, location) VALUES
            ('Computer Science', 'Block A'), ('Electronics', 'Block B'),
            ('Mathematics', 'Block C'), ('Physics', 'Block D');
        INSERT OR IGNORE INTO pincode VALUES
            ('600001','Chennai','Tamil Nadu'),
            ('600002','Chennai','Tamil Nadu'),
            ('600003','Chennai','Tamil Nadu'),
            ('400001','Mumbai','Maharashtra'),
            ('110001','Delhi','Delhi');
        INSERT OR IGNORE INTO student VALUES
            ('24BAI1001','Aryan','Sharma','2005-03-15','aryan@vit.ac.in','9876543210','12 Main St','600001',2,1),
            ('24BAI1002','Priya','Nair','2005-07-22','priya@vit.ac.in','9876543211','34 Park Ave','600002',2,1),
            ('24BAI1003','Rahul','Verma','2004-11-05','rahul@vit.ac.in','9876543212','56 Ring Rd','600003',3,2);
        INSERT OR IGNORE INTO instructor(name,email,phone,designation_id) VALUES
            ('Dr. Ramesh Kumar','ramesh@vit.ac.in','9900001111',1),
            ('Dr. Sunita Patel','sunita@vit.ac.in','9900002222',2),
            ('Prof. Anil Mehta','anil@vit.ac.in','9900003333',3);
        INSERT OR IGNORE INTO course VALUES
            ('CS101','Data Structures',4,'Odd',1),
            ('CS102','Database Management',3,'Even',1),
            ('EC101','Digital Circuits',4,'Odd',2),
            ('MA101','Linear Algebra',3,'Even',3);
        INSERT OR IGNORE INTO course_instructor(course_id,instructor_id) VALUES
            ('CS101',1),('CS102',2),('EC101',3),('MA101',2);
        INSERT OR IGNORE INTO course_textbook(course_id,textbook) VALUES
            ('CS101','Introduction to Algorithms — CLRS'),
            ('CS101','Data Structures Using C — Tanenbaum'),
            ('CS102','Database System Concepts — Silberschatz'),
            ('EC101','Digital Design — Morris Mano');
        INSERT OR IGNORE INTO enrollment(student_id,course_id,grade,enrollment_date) VALUES
            ('24BAI1001','CS101','A','2024-07-01'),
            ('24BAI1001','CS102','B+','2024-12-01'),
            ('24BAI1002','CS101','O','2024-07-01'),
            ('24BAI1003','EC101','A+','2024-07-01');
        """)

init_db()

@app.route("/")
def index(): return render_template("index.html")

def make_crud(table, pk, cols):
    def list_fn():
        with conn() as c: return jsonify(rows(c.execute(f"SELECT * FROM {table}")))
    def create_fn():
        data = request.json
        vals = [data.get(col) for col in cols]
        ph = ",".join(["?"]*len(cols)); col_str = ",".join(cols)
        with conn() as c:
            cur = c.execute(f"INSERT INTO {table}({col_str}) VALUES({ph})", vals)
            return jsonify({"id": data.get(pk, cur.lastrowid), "ok": True}), 201
    def update_fn(record_id):
        data = request.json
        sets = ", ".join([f"{aol}=?" for col in cols])
        vals = [data.get(col) for col in cols] + [record_id]
        with conn() as c: c.execute(f"UPDATE {table} SET {sets} WHERE {pk}=?", vals)
        return jsonify({"ok": True})
    def delete_fn(record_id):
        with conn() as c: c.execute(f"DELETE FROM {table} WHERE {pk}=?", [record_id])
        return jsonify({"ok": True})
    return list_fn, create_fn, update_fn, delete_fn

def reg(table, pk, cols, prefix, path, id_conv=None):
    l,cr,u,d = make_crud(table, pk, cols)
    app.add_url_rule(f"/api/{path}",                f"{prefix}_l",  l)
    app.add_url_rule(f"/api/{path}",                f"{prefix}_cr", cr, methods=["POST"])
    if id_conv=="int":
        app.add_url_rule(f"/api/{path}/<int:i>", f"{prefix}_u", u, methods=["PUT"])
        app.add_url_rule(f"/api/{path}/<int:i>", f"{prefix}_d", d, methods=["DELETE"])
    else:
        app.add_url_rule(f"/api/{path}/<i>", f"{prefix}_u", u, methods=["PUT"])
        app.add_url_rule(f"/api/{path}/<i>", f"{prefix}_d", d, methods=["DELETE"])

reg("department","department_id",["department_name","location"],"dept","departments","int")
reg("designation","designation_id",["designation_name","base_salary"],"desig","designations","int")
reg("pincode","pincode",["pincode","city","state"],"pin","pincodes")
reg("student","student_id",["student_id","first_name","last_name","dob","email","phone","street","pincode","year_of_study","department_id"],"stud","students")
reg("instructor","instructor_id",["name","email","phone","designation_id"],"inst","instructors","int")
reg("course","course_id",["course_id","course_name","credits","semester","department_id"],"crs","courses")
reg("course_instructor","id",["course_id","instructor_id"],"ci","course-instructors","int")
reg("course_textbook","id",["course_id","textbook"],"ct","course-textbooks","int")
reg("enrollment","enrollment_id",["student_id","course_id","grade","enrollment_date"],"enr","enrollments","int")

@app.route("/api/students/full")
def students_full():
    with conn() as c:
        return jsonify(rows(c.execute("""
            SELECT s.*, p.city, p.state, d.department_name
            FROM student s LEFT JOIN pincode p USING(pincode) LEFT JOIN department d USING(department_id)""")))

@app.route("/api/instructors/full")
def instructors_full():
    with conn() as c:
        return jsonify(rows(c.execute("""
            SELECT i.*, dg.designation_name, dg.base_salary
            FROM instructor i LEFT JOIN designation dg USING(designation_id)""")))

@app.route("/api/enrollments/full")
def enrollments_full():
    with conn() as c:
        return jsonify(rows(c.execute("""
            SELECT e.*, s.first_name||' '||s.last_name AS student_name, c.course_name
            FROM enrollment e LEFT JOIN student s USING(student_id) LEFT JOIN course c USING(course_id)""")))

@app.route("/api/courses/full")
def courses_full():
    with conn() as c:
        return jsonify(rows(c.execute("""
            SELECT c.*, d.department_name FROM course c LEFT JOIN department d USING(department_id)""")))

@app.route("/api/course-instructors/full")
def ci_full():
    with conn() as c:
        return jsonify(rows(c.execute("""
            SELECT ci.id, ci.course_id, ci.instructor_id, c.course_name, i.name AS instructor_name
            FROM course_instructor ci LEFT JOIN course c USING(course_id) LEFT JOIN instructor i USING(instructor_id)""")))

@app.route("/api/course-textbooks/full")
def ct_full():
    with conn() as c:
        return jsonify(rows(c.execute("""
            SELECT ct.id, ct.course_id, ct.textbook, c.course_name
            FROM course_textbook ct LEFT JOIN course c USING(course_id)""")))

if __name__ == "__main__":
    app.run(debug=True, port=5000)

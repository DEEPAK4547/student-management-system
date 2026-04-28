from flask import Flask, render_template, jsonify, request
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'deepak01',
    'database': 'student_management'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Database error: {e}")
        return None

# ==================== FRONTEND ====================
@app.route('/')
def index():
    return render_template('dashboard.html')

# ==================== STATS API ====================
@app.route('/api/stats')
def api_stats():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cur = conn.cursor(dictionary=True)
    stats = {}
    cur.execute("SELECT COUNT(*) AS c FROM students")
    stats['total_students'] = cur.fetchone()['c']
    cur.execute("SELECT COUNT(*) AS c FROM courses")
    stats['total_courses'] = cur.fetchone()['c']
    cur.execute("SELECT COUNT(*) AS c FROM instructors")
    stats['total_instructors'] = cur.fetchone()['c']
    cur.execute("SELECT ROUND(AVG(cgpa),2) AS avg FROM students WHERE status='Active'")
    stats['avg_cgpa'] = float(cur.fetchone()['avg'] or 0)
    cur.close()
    conn.close()
    return jsonify(stats)

# ==================== STUDENTS CRUD ====================
@app.route('/api/students', methods=['GET'])
def get_students():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT s.student_id, CONCAT(s.first_name,' ',s.last_name) AS name,
        s.first_name, s.last_name, s.email, s.phone, s.date_of_birth, s.gender,
        s.status, s.cgpa, d.dept_name, s.dept_id
        FROM students s
        LEFT JOIN departments d ON s.dept_id=d.dept_id
        ORDER BY s.last_name
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(data)

@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.json
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO students (first_name, last_name, email, phone, date_of_birth, gender, dept_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'Active')
        """, (data['first_name'], data['last_name'], data['email'], data.get('phone'), data.get('date_of_birth'), data.get('gender'), data.get('dept_id')))
        conn.commit()
        new_id = cur.lastrowid
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Student added', 'student_id': new_id})
    except Error as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.json
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE students SET first_name=%s, last_name=%s, email=%s, phone=%s,
            date_of_birth=%s, gender=%s, dept_id=%s, status=%s
            WHERE student_id=%s
        """, (data['first_name'], data['last_name'], data['email'], data.get('phone'), data.get('date_of_birth'), data.get('gender'), data.get('dept_id'), data.get('status', 'Active'), id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Student updated'})
    except Error as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM students WHERE student_id=%s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Student deleted'})
    except Error as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 400

# ==================== COURSES CRUD ====================
@app.route('/api/courses', methods=['GET'])
def get_courses():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT c.course_id, c.course_code, c.course_name, c.credits, c.semester, c.year,
        c.max_capacity, c.status, c.description, CONCAT(i.first_name,' ',i.last_name) AS instructor, c.instructor_id
        FROM courses c
        LEFT JOIN instructors i ON c.instructor_id=i.instructor_id
        ORDER BY c.course_code
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(data)

@app.route('/api/courses', methods=['POST'])
def add_course():
    data = request.json
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO courses (course_code, course_name, credits, dept_id, instructor_id, semester, year, max_capacity, description, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Open')
        """, (data['course_code'], data['course_name'], data['credits'], data.get('dept_id'), data.get('instructor_id'), data['semester'], data['year'], data.get('max_capacity', 30), data.get('description')))
        conn.commit()
        new_id = cur.lastrowid
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Course added', 'course_id': new_id})
    except Error as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/courses/<int:id>', methods=['PUT'])
def update_course(id):
    data = request.json
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE courses SET course_code=%s, course_name=%s, credits=%s, dept_id=%s,
            instructor_id=%s, semester=%s, year=%s, max_capacity=%s, description=%s, status=%s
            WHERE course_id=%s
        """, (data['course_code'], data['course_name'], data['credits'], data.get('dept_id'), data.get('instructor_id'), data['semester'], data['year'], data.get('max_capacity', 30), data.get('description'), data.get('status', 'Open'), id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Course updated'})
    except Error as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/courses/<int:id>', methods=['DELETE'])
def delete_course(id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM courses WHERE course_id=%s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Course deleted'})
    except Error as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 400

# ==================== ENROLLMENTS CRUD ====================
@app.route('/api/enrollments', methods=['GET'])
def get_enrollments():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT e.enrollment_id, CONCAT(s.first_name,' ',s.last_name) AS student, s.student_id,
        c.course_code, c.course_name, c.course_id, e.semester, e.year, e.status
        FROM enrollments e
        JOIN students s ON e.student_id=s.student_id
        JOIN courses c ON e.course_id=c.course_id
        ORDER BY e.enrollment_id
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(data)

@app.route('/api/enrollments', methods=['POST'])
def add_enrollment():
    data = request.json
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO enrollments (student_id, course_id, semester, year, status)
            VALUES (%s, %s, %s, %s, 'Enrolled')
        """, (data['student_id'], data['course_id'], data['semester'], data['year']))
        conn.commit()
        new_id = cur.lastrowid
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Enrollment added', 'enrollment_id': new_id})
    except Error as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/enrollments/<int:id>', methods=['PUT'])
def update_enrollment(id):
    data = request.json
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE enrollments SET student_id=%s, course_id=%s, semester=%s, year=%s, status=%s
            WHERE enrollment_id=%s
        """, (data['student_id'], data['course_id'], data['semester'], data['year'], data.get('status', 'Enrolled'), id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Enrollment updated'})
    except Error as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/enrollments/<int:id>', methods=['DELETE'])
def delete_enrollment(id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM enrollments WHERE enrollment_id=%s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Enrollment deleted'})
    except Error as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 400

# ==================== GRADES CRUD ====================
@app.route('/api/grades', methods=['GET'])
def get_grades():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT g.grade_id, CONCAT(s.first_name,' ',s.last_name) AS student,
        c.course_code, g.enrollment_id, g.assignment_score, g.midterm_score, g.final_score,
        g.total_score, g.letter_grade, g.grade_point, g.remarks
        FROM grades g
        JOIN enrollments e ON g.enrollment_id=e.enrollment_id
        JOIN students s ON e.student_id=s.student_id
        JOIN courses c ON e.course_id=c.course_id
        ORDER BY g.grade_id
    """)
    data = cur.fetchall()
    for row in data:
        for key in ['assignment_score','midterm_score','final_score','total_score','grade_point']:
            if row[key] is not None:
                row[key] = float(row[key])
    cur.close()
    conn.close()
    return jsonify(data)

@app.route('/api/grades', methods=['POST'])
def add_grade():
    data = request.json
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO grades (enrollment_id, assignment_score, midterm_score, final_score, remarks)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE assignment_score=%s, midterm_score=%s, final_score=%s, remarks=%s
        """, (data['enrollment_id'], data['assignment_score'], data['midterm_score'], data['final_score'], data.get('remarks', ''),
              data['assignment_score'], data['midterm_score'], data['final_score'], data.get('remarks', '')))
        conn.commit()
        new_id = cur.lastrowid
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Grade added/updated', 'grade_id': new_id})
    except Error as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/grades/<int:id>', methods=['DELETE'])
def delete_grade(id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM grades WHERE grade_id=%s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Grade deleted'})
    except Error as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 400

# ==================== INSTRUCTORS & DEPARTMENTS READ-ONLY ====================
@app.route('/api/instructors', methods=['GET'])
def get_instructors():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT instructor_id, CONCAT(first_name,' ',last_name) AS name, email, designation, salary, status, dept_id FROM instructors ORDER BY last_name")
    data = cur.fetchall()
    for row in data:
        if row['salary'] is not None:
            row['salary'] = float(row['salary'])
    cur.close()
    conn.close()
    return jsonify(data)

@app.route('/api/departments', methods=['GET'])
def get_departments():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT d.dept_id, d.dept_name, d.dept_code, d.location,
        COUNT(DISTINCT s.student_id) AS total_students,
        COUNT(DISTINCT i.instructor_id) AS total_instructors,
        COUNT(DISTINCT c.course_id) AS total_courses,
        ROUND(AVG(s.cgpa),2) AS avg_cgpa
        FROM departments d
        LEFT JOIN students s ON d.dept_id=s.dept_id AND s.status='Active'
        LEFT JOIN instructors i ON d.dept_id=i.dept_id AND i.status='Active'
        LEFT JOIN courses c ON d.dept_id=c.dept_id
        GROUP BY d.dept_id, d.dept_name, d.dept_code, d.location
        ORDER BY d.dept_name
    """)
    data = cur.fetchall()
    for row in data:
        if row['avg_cgpa'] is not None:
            row['avg_cgpa'] = float(row['avg_cgpa'])
        else:
            row['avg_cgpa'] = 0
    cur.close()
    conn.close()
    return jsonify(data)

# ==================== SQL PARSER HELPER ====================
def parse_sql_statements(sql_content):
    """Parse SQL file respecting DELIMITER changes (needed for procedures/triggers)."""
    statements = []
    delimiter = ';'
    buffer = []
    lines = sql_content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        # Handle DELIMITER command (case-insensitive)
        if stripped.upper().startswith('DELIMITER'):
            parts = stripped.split()
            if len(parts) >= 2:
                # Flush any buffered statement before changing delimiter
                if buffer:
                    stmt = '\n'.join(buffer).strip()
                    if stmt:
                        statements.append(stmt)
                    buffer = []
                delimiter = parts[1]
            i += 1
            continue
        buffer.append(line)
        # Check if line ends with the current delimiter
        if stripped.endswith(delimiter):
            # Remove the trailing delimiter for execution
            buffer[-1] = line.rstrip()[:-len(delimiter)].rstrip()
            stmt = '\n'.join(buffer).strip()
            if stmt and not stmt.upper().startswith('DELIMITER'):
                statements.append(stmt)
            buffer = []
        i += 1
    # Flush remaining buffer
    if buffer:
        stmt = '\n'.join(buffer).strip()
        if stmt:
            statements.append(stmt)
    return statements

# ==================== RESTORE ALL RECORDS ====================
@app.route('/api/restore', methods=['POST'])
def restore_all_records():
    """Restore database to original state by re-running all SQL scripts"""
    import os
    
    # Files to execute in order
    sql_files = [
        'schema.sql',
        'seed_data.sql', 
        'procedures_functions.sql',
        'triggers.sql'
    ]
    
    # Connect without database first to allow schema recreation
    config_no_db = DB_CONFIG.copy()
    config_no_db.pop('database', None)
    
    try:
        conn = mysql.connector.connect(**config_no_db)
        cur = conn.cursor()
        
        for sql_file in sql_files:
            if not os.path.exists(sql_file):
                return jsonify({'success': False, 'error': f'SQL file not found: {sql_file}'}), 500
            
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            statements = parse_sql_statements(sql_content)
            for stmt in statements:
                # Skip comments and empty lines
                if not stmt or stmt.startswith('--') or stmt.startswith('/*') or stmt.startswith('*'):
                    continue
                try:
                    cur.execute(stmt)
                    conn.commit()
                except Error as e:
                    # Some statements may fail if they already exist, continue
                    print(f"Note in {sql_file}: {e}")
                    conn.rollback()
        
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'All records restored successfully! Database reset to original state.'})
    except Error as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


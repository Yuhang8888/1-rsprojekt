from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        dbname='Tanbajan',
        user='postgres',
        password='2011',
        host='localhost',
        port='5432',
    )
    return conn

def get_employees():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, first_name || ' ' || last_name, job_title FROM employees ORDER BY first_name;")
    employees = cur.fetchall()
    conn.close()
    return employees

# In-memory schedule storage for display only
schedule_entries = []

@app.route('/', methods=['GET', 'POST'])
def schedule():
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    employees = get_employees()

    # Time slots every half hour from 7:00 to 20:00
    times = []
    hour, minute = 7, 0
    while hour < 20 or (hour == 20 and minute == 0):
        times.append(f"{hour:02d}:{minute:02d}")
        minute += 30
        if minute == 60:
            hour += 1
            minute = 0

    durations = [str(dur) for dur in [x * 0.5 for x in range(1, 27)]]

    if request.method == 'POST':
        # Accept up to 5 shift entries indexed 0 to 4
        for i in range(5):
            emp_id = request.form.get(f'employee_{i}')
            day = request.form.get(f'day_{i}')
            start_time = request.form.get(f'start_{i}')
            duration = request.form.get(f'duration_{i}')
            if emp_id and day and start_time and duration:
                emp_id = int(emp_id)

                # Insert into employee_hours table
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO employee_hours (employee_id, day, start_time, duration)
                    VALUES (%s, %s, %s, %s)
                """, (
                    emp_id,
                    day,
                    start_time,
                    float(duration)
                ))
                conn.commit()
                cur.close()
                conn.close()

                # Add to in-memory schedule for display (optional)
                emp_data = next((e for e in employees if e[0] == emp_id), None)
                if emp_data:
                    schedule_entries.append({
                        'employee_id': emp_id,
                        'employee_name': emp_data[1],
                        'job_title': emp_data[2],
                        'day': day,
                        'start_time': start_time,
                        'duration': duration,
                    })

        return redirect(url_for('schedule'))

    # Organize schedule by (employee_id, day) for rendering
    schedule_dict = {}
    for entry in schedule_entries:
        key = (entry['employee_id'], entry['day'])
        schedule_dict.setdefault(key, []).append(entry)

    return render_template('schedule.html', employees=employees, days=days,
                           times=times, durations=durations, schedule_dict=schedule_dict)

if __name__ == '__main__':
    app.run(debug=True)

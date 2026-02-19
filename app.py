from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 date TEXT,
                 hour TEXT,
                 status TEXT,
                 time_marked TEXT
                 )''')
    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def index():
    init_db()
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()

    if request.method == "POST":
        date = datetime.now().strftime("%Y-%m-%d")
        hour = request.form["hour"]
        status = request.form["status"]
        time_marked = datetime.now().strftime("%H:%M:%S")

        c.execute("SELECT * FROM attendance WHERE date=? AND hour=?", (date, hour))
        existing = c.fetchone()

        if not existing:
            c.execute("INSERT INTO attendance (date, hour, status, time_marked) VALUES (?, ?, ?, ?)",
                      (date, hour, status, time_marked))
            conn.commit()

        return redirect("/")

    today = datetime.now().strftime("%Y-%m-%d")

    # Today's records
    c.execute("SELECT * FROM attendance WHERE date=? ORDER BY hour", (today,))
    today_records = c.fetchall()

    # All records
    c.execute("SELECT * FROM attendance ORDER BY date DESC, hour ASC")
    all_records = c.fetchall()

    # Daily percentage
    total_today = len(today_records)
    present_today = len([r for r in today_records if r[3] == "Present"])
    daily_percentage = round((present_today / total_today) * 100, 2) if total_today > 0 else 0

    # Overall percentage
    total_all = len(all_records)
    present_all = len([r for r in all_records if r[3] == "Present"])
    overall_percentage = round((present_all / total_all) * 100, 2) if total_all > 0 else 0

    conn.close()

    return render_template("index.html",
                           today_records=today_records,
                           all_records=all_records,
                           daily_percentage=daily_percentage,
                           overall_percentage=overall_percentage)

if __name__ == "__main__":
    app.run(debug=True)

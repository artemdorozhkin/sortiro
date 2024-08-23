from datetime import datetime
import sqlite3

conn = sqlite3.connect("time_tracking.db")
cursor = conn.cursor()

cursor.execute(
    """CREATE TABLE IF NOT EXISTS time_tracking (
                    user_id INTEGER,
                    start_time TEXT,
                    end_time TEXT,
                    duration INTEGER
                  )"""
)
conn.commit()


def get_timer(user_id: int):
    cursor.execute(
        "SELECT start_time FROM time_tracking WHERE user_id = ? AND end_time IS NULL",
        (user_id,),
    )
    return cursor.fetchone()


def create_timer(user_id: int, start_time: datetime):
    cursor.execute(
        "INSERT INTO time_tracking (user_id, start_time) VALUES (?, ?)",
        (user_id, start_time),
    )
    conn.commit()


def stop_timer(user_id: int, end_time: datetime, duration: int):
    cursor.execute(
        "UPDATE time_tracking SET end_time = ?, duration = ? WHERE user_id = ? AND end_time IS NULL",
        (end_time, duration, user_id),
    )
    conn.commit()


def get_stat_by_period(user_id: int, period: datetime):
    cursor.execute(
        "SELECT SUM(duration), COUNT(duration) FROM time_tracking WHERE user_id = ? AND start_time >= ?",
        (user_id, period),
    )
    return cursor.fetchone()


def get_stats(user_id: int):
    cursor.execute(
        "SELECT SUM(duration), COUNT(duration) FROM time_tracking WHERE user_id = ?",
        (user_id,),
    )
    return cursor.fetchone()

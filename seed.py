from app import app, db, Event

with app.app_context():
    # Add one sample event
    sample = Event(
        title="Misa di Santa Maria",
        location="Paradera",
        date="2024-12-25",
        time="10:00 AM",
        description="Sample event from Python backend!",
        type="Mass"
    )
    db.session.add(sample)
    db.session.commit()
    print("Database seeded! Now refresh your browser.")
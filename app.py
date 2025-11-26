from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = "supersecretkey"

# TRAIN DATABASE
trains = {
    "Rajdhani Express": {"capacity": 10, "booked": [], "waiting": []},
    "Shatabdi Express": {"capacity": 10, "booked": [], "waiting": []},
    "Duronto Express": {"capacity": 10, "booked": [], "waiting": []},
    "Garib Rath": {"capacity": 10, "booked": [], "waiting": []},
    "Passenger Local": {"capacity": 1, "booked": [], "waiting": []}
}

# ---------------- Login ----------------
@app.route('/')
def login_page():
    return redirect('/login')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == "admin" and request.form['password'] == "123":
            session['logged_in'] = True
            return redirect('/home')
        return render_template('login.html', msg="Invalid credentials")
    return render_template('login.html')

# ---------------- Home ----------------
@app.route('/home')
def home():
    if not session.get('logged_in'):
        return redirect('/login')
    return render_template('index.html')

# ---------------- Book Ticket ----------------
@app.route('/book', methods=['GET','POST'])
def book():
    if not session.get('logged_in'):
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        train_name = request.form['train']

        train = trains[train_name]

        # Generate unique PNR
        pnr = f"{train_name[:3].upper()}{random.randint(1000,9999)}"

        # Confirmed booking
        if len(train["booked"]) < train["capacity"]:
            seat_no = len(train["booked"]) + 1
            train["booked"].append({
                "name": name,
                "age": age,
                "seat": seat_no,
                "train": train_name,
                "status": "Confirmed",
                "pnr": pnr
            })
            return render_template('message.html', message=f"Ticket booked successfully! Seat No: {seat_no}, PNR: {pnr}")

        # Waiting list
        w_no = len(train["waiting"]) + 1
        train["waiting"].append({
            "name": name,
            "age": age,
            "seat": f"W{w_no}",
            "train": train_name,
            "status": "Waiting",
            "pnr": pnr
        })
        return render_template('message.html', message=f"Train Full! Added to Waiting List: W{w_no}, PNR: {pnr}")

    return render_template('book.html', trains=list(trains.keys()))

# ---------------- View Tickets ----------------
@app.route('/view')
def view():
    if not session.get('logged_in'):
        return redirect('/login')

    all_tickets = []
    for train in trains.values():
        all_tickets += train["booked"] + train["waiting"]

    return render_template('view.html', tickets=all_tickets)

# ---------------- Cancel Ticket ----------------
@app.route('/cancel', methods=['GET','POST'])
def cancel():
    if not session.get('logged_in'):
        return redirect('/login')

    if request.method == 'POST':
        pnr_input = request.form['pnr']
        found = False

        for train_name, train in trains.items():
            # Confirmed tickets
            for t in train["booked"]:
                if t["pnr"] == pnr_input:
                    train["booked"].remove(t)
                    found = True
                    # Promote waiting list
                    if train["waiting"]:
                        promote = train["waiting"].pop(0)
                        promote["status"] = "Confirmed"
                        promote["seat"] = len(train["booked"]) + 1
                        train["booked"].append(promote)
                    return render_template('message.html', message=f"Ticket with PNR {pnr_input} cancelled successfully!")

            # Waiting list
            for t in train["waiting"]:
                if t["pnr"] == pnr_input:
                    train["waiting"].remove(t)
                    found = True
                    return render_template('message.html', message=f"Waiting list ticket with PNR {pnr_input} cancelled!")

        if not found:
            return render_template('message.html', message="No ticket found with this PNR!")

    return render_template('cancel.html')

# ---------------- Logout ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ---------------- Run ----------------
if __name__ == "__main__":
    app.run(debug=True)

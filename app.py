from flask import Flask, request, redirect, url_for, session, render_template_string
import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Secret key for login sessions
app.secret_key = "atm_management_system_2026"

# Database file
DATABASE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "atm_database.db"
)


# =========================================================
# DATABASE
# =========================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_database():

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_number TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            pin TEXT NOT NULL,
            balance REAL NOT NULL DEFAULT 0
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_number TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            transaction_date TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# GENERATE ACCOUNT NUMBER
# =========================================================

def generate_account_number():

    conn = get_db()

    row = conn.execute(
        "SELECT account_number FROM users ORDER BY id DESC LIMIT 1"
    ).fetchone()

    conn.close()

    if row is None:
        return "1001"

    try:
        return str(int(row["account_number"]) + 1)
    except:
        return "1001"


# =========================================================
# HTML DESIGN
# =========================================================

HTML = """
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>ATM Management System</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: linear-gradient(135deg, #141e30, #243b55);
    min-height: 100vh;
    color: #222;
}

.navbar {
    background: #111827;
    color: white;
    padding: 18px 30px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.navbar h2 {
    margin: 0;
}

.navbar a {
    color: white;
    text-decoration: none;
    margin-left: 20px;
}

.container {
    width: 90%;
    max-width: 1000px;
    margin: 40px auto;
}

.card {
    background: white;
    border-radius: 15px;
    padding: 30px;
    margin-bottom: 25px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}

.center {
    text-align: center;
}

h1 {
    color: #111827;
}

h2 {
    color: #1f2937;
}

input {
    width: 100%;
    padding: 13px;
    margin: 8px 0 15px;
    border: 1px solid #ccc;
    border-radius: 8px;
    font-size: 16px;
}

button {
    width: 100%;
    padding: 13px;
    border: none;
    border-radius: 8px;
    background: #2563eb;
    color: white;
    font-size: 16px;
    cursor: pointer;
}

button:hover {
    background: #1d4ed8;
}

.menu {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
}

.menu a {
    text-decoration: none;
}

.menu button {
    height: 70px;
}

.balance {
    font-size: 40px;
    font-weight: bold;
    color: #16a34a;
    text-align: center;
    margin: 25px;
}

.message {
    padding: 15px;
    background: #fee2e2;
    color: #991b1b;
    border-radius: 8px;
    margin-bottom: 15px;
}

.success {
    padding: 15px;
    background: #dcfce7;
    color: #166534;
    border-radius: 8px;
    margin-bottom: 15px;
}

.info {
    padding: 15px;
    background: #dbeafe;
    color: #1e40af;
    border-radius: 8px;
    margin-bottom: 15px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

th, td {
    padding: 12px;
    border-bottom: 1px solid #ddd;
    text-align: left;
}

th {
    background: #111827;
    color: white;
}

.deposit {
    color: green;
    font-weight: bold;
}

.withdraw {
    color: red;
    font-weight: bold;
}

.account-number {
    font-size: 25px;
    font-weight: bold;
    color: #2563eb;
}

@media(max-width: 650px) {

    .menu {
        grid-template-columns: 1fr;
    }

    .navbar {
        flex-direction: column;
        gap: 10px;
    }

}

</style>

</head>

<body>

<div class="navbar">

<h2>🏦 ATM Management System</h2>

<div>

{% if session.get("account_number") %}

<a href="{{ url_for('dashboard') }}">Dashboard</a>

<a href="{{ url_for('logout') }}">Logout</a>

{% else %}

<a href="{{ url_for('home') }}">Home</a>

{% endif %}

</div>

</div>


<div class="container">

{{ content|safe }}

</div>

</body>

</html>
"""


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    content = """

    <div class="card center">

        <h1>🏦 ATM MANAGEMENT SYSTEM</h1>

        <p>
        Welcome to the Online ATM Management System
        </p>

        <br>

        <div class="menu">

            <a href="/create">
                <button>Create New Account</button>
            </a>

            <a href="/login">
                <button>Login</button>
            </a>

        </div>

    </div>

    """

    return render_template_string(
        HTML,
        content=content
    )


# =========================================================
# CREATE ACCOUNT
# =========================================================

@app.route("/create", methods=["GET", "POST"])
def create():

    message = ""

    if request.method == "POST":

        name = request.form["name"].strip()
        pin = request.form["pin"].strip()
        amount_text = request.form["amount"].strip()

        if not name:

            message = """
            <div class="message">
            Please enter your name.
            </div>
            """

        elif len(pin) != 4 or not pin.isdigit():

            message = """
            <div class="message">
            PIN must contain exactly 4 digits.
            </div>
            """

        else:

            try:

                amount = float(amount_text)

                if amount < 0:
                    raise ValueError

                account_number = generate_account_number()

                conn = get_db()

                conn.execute(
                    """
                    INSERT INTO users
                    (account_number, name, pin, balance)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        account_number,
                        name,
                        generate_password_hash(pin),
                        amount
                    )
                )

                if amount > 0:

                    conn.execute(
                        """
                        INSERT INTO transactions
                        (account_number, transaction_type,
                         amount, transaction_date)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            account_number,
                            "Initial Deposit",
                            amount,
                            datetime.now().strftime(
                                "%d-%m-%Y %H:%M:%S"
                            )
                        )
                    )

                conn.commit()
                conn.close()

                content = f"""

                <div class="card center">

                    <h1>✅ Account Created Successfully!</h1>

                    <p>Your account has been created.</p>

                    <p>Account Holder</p>

                    <div class="account-number">
                    {name}
                    </div>

                    <p>Account Number</p>

                    <div class="account-number">
                    {account_number}
                    </div>

                    <p>
                    Initial Balance:
                    <b>Rs.{amount:.2f}</b>
                    </p>

                    <br>

                    <div class="info">
                    ⚠️ Please remember your Account Number.
                    </div>

                    <a href="/login">
                    <button>Go to Login</button>
                    </a>

                </div>

                """

                return render_template_string(
                    HTML,
                    content=content
                )

            except ValueError:

                message = """
                <div class="message">
                Please enter a valid deposit amount.
                </div>
                """


    content = f"""

    <div class="card">

        <h1>👤 Create New Account</h1>

        {message}

        <form method="POST">

            <label>Name</label>

            <input
                type="text"
                name="name"
                placeholder="Enter your name"
                required
            >

            <label>4-Digit PIN</label>

            <input
                type="password"
                name="pin"
                maxlength="4"
                placeholder="Enter 4-digit PIN"
                required
            >

            <label>Initial Deposit</label>

            <input
                type="number"
                name="amount"
                min="0"
                step="0.01"
                placeholder="Enter initial deposit"
                required
            >

            <button type="submit">
                Create Account
            </button>

        </form>

        <br>

        <a href="/login">
        Already have an account? Login
        </a>

    </div>

    """

    return render_template_string(
        HTML,
        content=content
    )


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    message = ""

    if request.method == "POST":

        account_number = request.form["account_number"].strip()
        pin = request.form["pin"].strip()

        conn = get_db()

        user = conn.execute(
            """
            SELECT * FROM users
            WHERE account_number = ?
            """,
            (account_number,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(
            user["pin"],
            pin
        ):

            session["account_number"] = account_number

            return redirect(
                url_for("dashboard")
            )

        else:

            message = """
            <div class="message">
            ❌ Invalid Account Number or PIN.
            </div>
            """


    content = f"""

    <div class="card">

        <h1>🔐 Login</h1>

        {message}

        <form method="POST">

            <label>Account Number</label>

            <input
                type="text"
                name="account_number"
                placeholder="Example: 1001"
                required
            >

            <label>PIN</label>

            <input
                type="password"
                name="pin"
                maxlength="4"
                placeholder="Enter PIN"
                required
            >

            <button type="submit">
                Login
            </button>

        </form>

        <br>

        <a href="/create">
        Create New Account
        </a>

    </div>

    """

    return render_template_string(
        HTML,
        content=content
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "account_number" not in session:
        return redirect(url_for("login"))

    account_number = session["account_number"]

    conn = get_db()

    user = conn.execute(
        """
        SELECT * FROM users
        WHERE account_number = ?
        """,
        (account_number,)
    ).fetchone()

    conn.close()

    if user is None:

        session.clear()

        return redirect(
            url_for("login")
        )


    content = f"""

    <div class="card center">

        <h1>Welcome, {user["name"]}! 👋</h1>

        <p>
        Account Number:
        <b>{user["account_number"]}</b>
        </p>

        <div class="balance">
        Rs.{user["balance"]:.2f}
        </div>

        <p>Available Balance</p>

    </div>


    <div class="card">

        <h2>ATM Services</h2>

        <div class="menu">

            <a href="/balance">
            <button>💰 Check Balance</button>
            </a>

            <a href="/deposit">
            <button>➕ Deposit Money</button>
            </a>

            <a href="/withdraw">
            <button>➖ Withdraw Money</button>
            </a>

            <a href="/statement">
            <button>📜 Mini Statement</button>
            </a>

            <a href="/change-pin">
            <button>🔑 Change PIN</button>
            </a>

            <a href="/logout">
            <button>🚪 Logout</button>
            </a>

        </div>

    </div>

    """

    return render_template_string(
        HTML,
        content=content
    )


# =========================================================
# BALANCE
# =========================================================

@app.route("/balance")
def balance():

    if "account_number" not in session:
        return redirect(url_for("login"))

    account_number = session["account_number"]

    conn = get_db()

    user = conn.execute(
        """
        SELECT * FROM users
        WHERE account_number = ?
        """,
        (account_number,)
    ).fetchone()

    conn.close()

    content = f"""

    <div class="card center">

        <h1>💰 Check Balance</h1>

        <p>
        Account Holder:
        <b>{user["name"]}</b>
        </p>

        <p>
        Account Number:
        <b>{user["account_number"]}</b>
        </p>

        <div class="balance">
        Rs.{user["balance"]:.2f}
        </div>

        <p>Available Balance</p>

        <br>

        <a href="/dashboard">
        <button>Back to Dashboard</button>
        </a>

    </div>

    """

    return render_template_string(
        HTML,
        content=content
    )


# =========================================================
# DEPOSIT
# =========================================================

@app.route("/deposit", methods=["GET", "POST"])
def deposit():

    if "account_number" not in session:
        return redirect(url_for("login"))

    account_number = session["account_number"]

    message = ""

    if request.method == "POST":

        try:

            amount = float(
                request.form["amount"]
            )

            if amount <= 0:
                raise ValueError

            conn = get_db()

            conn.execute(
                """
                UPDATE users
                SET balance = balance + ?
                WHERE account_number = ?
                """,
                (amount, account_number)
            )

            conn.execute(
                """
                INSERT INTO transactions
                (account_number, transaction_type,
                 amount, transaction_date)
                VALUES (?, ?, ?, ?)
                """,
                (
                    account_number,
                    "Deposit",
                    amount,
                    datetime.now().strftime(
                        "%d-%m-%Y %H:%M:%S"
                    )
                )
            )

            conn.commit()
            conn.close()

            message = f"""
            <div class="success">
            ✅ Deposit successful!
            <br>
            Deposited: Rs.{amount:.2f}
            </div>
            """

        except ValueError:

            message = """
            <div class="message">
            Please enter a valid amount.
            </div>
            """


    content = f"""

    <div class="card">

        <h1>➕ Deposit Money</h1>

        {message}

        <form method="POST">

            <label>Amount</label>

            <input
                type="number"
                name="amount"
                min="0.01"
                step="0.01"
                placeholder="Enter amount"
                required
            >

            <button type="submit">
            Deposit
            </button>

        </form>

        <br>

        <a href="/dashboard">
        Back to Dashboard
        </a>

    </div>

    """

    return render_template_string(
        HTML,
        content=content
    )


# =========================================================
# WITHDRAW
# =========================================================

@app.route("/withdraw", methods=["GET", "POST"])
def withdraw():

    if "account_number" not in session:
        return redirect(url_for("login"))

    account_number = session["account_number"]

    message = ""

    if request.method == "POST":

        try:

            amount = float(
                request.form["amount"]
            )

            if amount <= 0:
                raise ValueError

            conn = get_db()

            user = conn.execute(
                """
                SELECT balance FROM users
                WHERE account_number = ?
                """,
                (account_number,)
            ).fetchone()

            if amount > user["balance"]:

                message = """
                <div class="message">
                ❌ Insufficient balance.
                </div>
                """

                conn.close()

            else:

                conn.execute(
                    """
                    UPDATE users
                    SET balance = balance - ?
                    WHERE account_number = ?
                    """,
                    (amount, account_number)
                )

                conn.execute(
                    """
                    INSERT INTO transactions
                    (account_number, transaction_type,
                     amount, transaction_date)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        account_number,
                        "Withdrawal",
                        amount,
                        datetime.now().strftime(
                            "%d-%m-%Y %H:%M:%S"
                        )
                    )
                )

                conn.commit()
                conn.close()

                message = f"""
                <div class="success">
                ✅ Withdrawal successful!
                <br>
                Withdrawn: Rs.{amount:.2f}
                </div>
                """

        except ValueError:

            message = """
            <div class="message">
            Please enter a valid amount.
            </div>
            """


    content = f"""

    <div class="card">

        <h1>➖ Withdraw Money</h1>

        {message}

        <form method="POST">

            <label>Amount</label>

            <input
                type="number"
                name="amount"
                min="0.01"
                step="0.01"
                placeholder="Enter amount"
                required
            >

            <button type="submit">
            Withdraw
            </button>

        </form>

        <br>

        <a href="/dashboard">
        Back to Dashboard
        </a>

    </div>

    """

    return render_template_string(
        HTML,
        content=content
    )


# =========================================================
# MINI STATEMENT
# =========================================================

@app.route("/statement")
def statement():

    if "account_number" not in session:
        return redirect(url_for("login"))

    account_number = session["account_number"]

    conn = get_db()

    user = conn.execute(
        """
        SELECT * FROM users
        WHERE account_number = ?
        """,
        (account_number,)
    ).fetchone()

    transactions = conn.execute(
        """
        SELECT * FROM transactions
        WHERE account_number = ?
        ORDER BY id DESC
        """,
        (account_number,)
    ).fetchall()

    conn.close()

    rows = ""

    for transaction in transactions:

        if transaction["transaction_type"] in [
            "Deposit",
            "Initial Deposit"
        ]:

            css_class = "deposit"

        else:

            css_class = "withdraw"


        rows += f"""

        <tr>

            <td>
            {transaction["transaction_date"]}
            </td>

            <td class="{css_class}">
            {transaction["transaction_type"]}
            </td>

            <td>
            Rs.{transaction["amount"]:.2f}
            </td>

        </tr>

        """


    content = f"""

    <div class="card">

        <h1>📜 Mini Statement</h1>

        <p>
        Account Holder:
        <b>{user["name"]}</b>
        </p>

        <p>
        Account Number:
        <b>{user["account_number"]}</b>
        </p>

        <table>

            <tr>

                <th>Date & Time</th>
                <th>Transaction</th>
                <th>Amount</th>

            </tr>

            {rows}

        </table>

        <br>

        <div class="balance">
        Rs.{user["balance"]:.2f}
        </div>

        <p class="center">
        Current Balance
        </p>

        <a href="/dashboard">
        <button>Back to Dashboard</button>
        </a>

    </div>

    """

    return render_template_string(
        HTML,
        content=content
    )


# =========================================================
# CHANGE PIN
# =========================================================

@app.route("/change-pin", methods=["GET", "POST"])
def change_pin():

    if "account_number" not in session:
        return redirect(url_for("login"))

    account_number = session["account_number"]

    message = ""

    if request.method == "POST":

        old_pin = request.form["old_pin"].strip()
        new_pin = request.form["new_pin"].strip()
        confirm_pin = request.form["confirm_pin"].strip()

        conn = get_db()

        user = conn.execute(
            """
            SELECT pin FROM users
            WHERE account_number = ?
            """,
            (account_number,)
        ).fetchone()

        if not check_password_hash(
            user["pin"],
            old_pin
        ):

            message = """
            <div class="message">
            ❌ Current PIN is incorrect.
            </div>
            """

            conn.close()

        elif len(new_pin) != 4 or not new_pin.isdigit():

            message = """
            <div class="message">
            New PIN must contain exactly 4 digits.
            </div>
            """

            conn.close()

        elif new_pin != confirm_pin:

            message = """
            <div class="message">
            ❌ New PINs do not match.
            </div>
            """

            conn.close()

        else:

            conn.execute(
                """
                UPDATE users
                SET pin = ?
                WHERE account_number = ?
                """,
                (
                    generate_password_hash(new_pin),
                    account_number
                )
            )

            conn.commit()
            conn.close()

            message = """
            <div class="success">
            ✅ PIN changed successfully!
            </div>
            """


    content = f"""

    <div class="card">

        <h1>🔑 Change PIN</h1>

        {message}

        <form method="POST">

            <label>Current PIN</label>

            <input
                type="password"
                name="old_pin"
                maxlength="4"
                required
            >

            <label>New PIN</label>

            <input
                type="password"
                name="new_pin"
                maxlength="4"
                required
            >

            <label>Confirm New PIN</label>

            <input
                type="password"
                name="confirm_pin"
                maxlength="4"
                required
            >

            <button type="submit">
            Change PIN
            </button>

        </form>

        <br>

        <a href="/dashboard">
        Back to Dashboard
        </a>

    </div>

    """

    return render_template_string(
        HTML,
        content=content
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    content = """

    <div class="card center">

        <h1>👋 Logged Out</h1>

        <p>
        You have been logged out successfully.
        </p>

        <br>

        <a href="/">
        <button>Return to Home</button>
        </a>

    </div>

    """

    return render_template_string(
        HTML,
        content=content
    )


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    create_database()

    print("")
    print("======================================")
    print("     ATM MANAGEMENT SYSTEM WEBSITE")
    print("======================================")
    print("")
    print("Website is starting...")
    print("")
    print("Open this address in your browser:")
    print("http://127.0.0.1:5000")
    print("")
    print("Press CTRL+C to stop the website.")
    print("======================================")

    app.run(debug=True)
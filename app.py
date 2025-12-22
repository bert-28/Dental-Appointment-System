# app.py
from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify, session
import sqlite3
import uuid
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

DB = "appointments.db"
APP = Flask(__name__)
APP.secret_key = "123456"
APP.config["SESSION_TYPE"] = "filesystem"

# ---------------- DATABASE ----------------
def get_conn(timeout=5):
    return sqlite3.connect(DB, timeout=timeout)

def init_db():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS patient (
                patient_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age TEXT,
                contact TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS dentist (
                dentist_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                specialty TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                appointment_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                dentist_id TEXT NOT NULL,
                service TEXT,
                date TEXT,
                time TEXT,
                status TEXT,
                created_at TEXT,
                FOREIGN KEY(patient_id) REFERENCES patient(patient_id),
                FOREIGN KEY(dentist_id) REFERENCES dentist(dentist_id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.commit()


# ---------------- METHODS ----------------
def generate_time_slots(start="08:00", end="18:00", interval_minutes=30):
    fmt = "%H:%M"
    s = datetime.strptime(start, fmt)
    e = datetime.strptime(end, fmt)
    slots = []
    cur = s
    while cur <= e:
        slots.append(cur.strftime("%I:%M %p"))
        cur += timedelta(minutes=interval_minutes)
    return slots

TIME_SLOTS = generate_time_slots()

def add_patient(name, age="", contact=""):
    pid = str(uuid.uuid4())
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO patient (patient_id,name,age,contact) VALUES (?,?,?,?)",
                  (pid, name, age, contact))
    return pid

def find_patient_by_name(name):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT patient_id,name,age,contact FROM patient WHERE name=?", (name,))
        return c.fetchone()

def add_dentist(name, specialty="General"):
    did = str(uuid.uuid4())
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO dentist (dentist_id,name,specialty) VALUES (?,?,?)", (did, name, specialty))
    return did

def get_dentists():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT dentist_id,name,specialty FROM dentist ORDER BY name")
        return c.fetchall()

def delete_dentist_by_id(did):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM dentist WHERE dentist_id = ?", (did,))

def add_appointment(patient_id, dentist_id, service, date, time_str):
    aid = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO appointments
            (appointment_id, patient_id, dentist_id, service, date, time, status, created_at)
            VALUES (?,?,?,?,?,?,?,?)
        """, (aid, patient_id, dentist_id, service, date, time_str, "pending", created_at))
    return aid

def get_appointments(search=""):
    with get_conn() as conn:
        c = conn.cursor()
        q = """
            SELECT a.appointment_id,
                   p.name, p.age, p.contact,
                   a.service, a.date, a.time,
                   d.name, d.specialty,
                   a.status
            FROM appointments a
            JOIN patient p ON a.patient_id = p.patient_id
            JOIN dentist d ON a.dentist_id = d.dentist_id
        """
        if search:
            q += " WHERE p.name LIKE ? OR d.name LIKE ? OR a.service LIKE ?"
            c.execute(q, (f"%{search}%", f"%{search}%", f"%{search}%"))
        else:
            c.execute(q)
        return c.fetchall()

def update_appointment_status(aid, status):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("UPDATE appointments SET status = ? WHERE appointment_id = ?", (status, aid))

def delete_appointment(aid):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM appointments WHERE appointment_id = ?", (aid,))

# ---------------- USERS ----------------
def register_user(name, email, password):
    uid = str(uuid.uuid4())
    hashed = generate_password_hash(password)
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO users (user_id,name,email,password) VALUES (?,?,?,?)",
                  (uid, name, email, hashed))
    return uid

def login_user(email, password):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT user_id,name,password FROM users WHERE email=?", (email,))
        user = c.fetchone()
        if user and check_password_hash(user[2], password):
            return user
    return None

# ---------- data access ----------
def add_patient(name, age="", contact=""):
    pid = str(uuid.uuid4())
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO patient (patient_id,name,age,contact) VALUES (?,?,?,?)",
            (pid, name, age, contact)
        )
    return pid


def add_patient(name, age="", contact=""):
    pid = str(uuid.uuid4())
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO patient (patient_id,name,age,contact) VALUES (?,?,?,?)",
            (pid, name, age, contact)
        )
    return pid


def add_dentist(name, specialty="General"):
    did = str(uuid.uuid4())
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO dentist (dentist_id,name,specialty) VALUES (?,?,?)",
            (did, name, specialty)
        )
    return did


def get_dentists():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            "SELECT dentist_id,name,specialty FROM dentist ORDER BY name"
        )
        return c.fetchall()


def delete_dentist_by_id(did):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            "DELETE FROM dentist WHERE dentist_id = ?",
            (did,)
        )

def add_appointment(patient_id, dentist_id, service, date, time_str):
    aid = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO appointments
            (appointment_id, patient_id, dentist_id, service, date, time, status, created_at)
            VALUES (?,?,?,?,?,?,?,?)
        """, (aid, patient_id, dentist_id, service, date, time_str, "pending", created_at))
    return aid

def get_appointments(search=""):
    with get_conn() as conn:
        c = conn.cursor()
        q = """
            SELECT a.appointment_id,
                   p.name, p.age, p.contact,
                   a.service, a.date, a.time,
                   d.name, d.specialty,
                   a.status
            FROM appointments a
            JOIN patient p ON a.patient_id = p.patient_id
            JOIN dentist d ON a.dentist_id = d.dentist_id
        """
        if search:
            q += " WHERE p.name LIKE ? OR d.name LIKE ? OR a.service LIKE ?"
            c.execute(q, (f"%{search}%", f"%{search}%", f"%{search}%"))
        else:
            c.execute(q)
        return c.fetchall()

def update_appointment_status(aid, status):
		with get_conn() as conn:
				c = conn.cursor()
				c.execute("UPDATE appointments SET status = ? WHERE id = ?", (status, aid))

def delete_appointment(aid):
		with get_conn() as conn:
				c = conn.cursor()
				c.execute("DELETE FROM appointments WHERE id = ?", (aid,))

# ---------- Flask templates ----------
BASE_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>Dental Appointment System</title>

<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

<style>
html {
	scroll-behavior: smooth;
}

body {
	background:#f3f6fb;
	font-size:15px;
}

.container-narrow {
	max-width:1200px;
	margin:auto;
}

/* NAV */
.navbar-brand {
	font-weight:700;
	color:#2563eb;
}

/* HERO */
.hero {
	background: linear-gradient(135deg, #2563eb, #60a5fa);
	color:white;
	border-radius:20px;
	padding:4rem 3rem;
}

/* SECTIONS */
.section {
	padding:4rem 0;
}

.section-light {
	background:#f8fafc;
}

.section-white {
	background:white;
}

.section h2 {
	font-weight:700;
	margin-bottom:1rem;
}

/* IMAGE CONTROL (FIXED SIZE) */
.section-img {
	width:100%;
	max-height:340px;
	object-fit:cover;
	border-radius:18px;
	box-shadow:0 10px 25px rgba(0,0,0,.08);
}

/* SERVICE ICONS */
.service-card {
	background:white;
	border-radius:16px;
	padding:1.5rem;
	text-align:center;
	box-shadow:0 6px 18px rgba(0,0,0,.06);
	height:100%;
}

/* TESTIMONIAL */
.testimonial {
	background:white;
	border-radius:16px;
	padding:1.5rem;
	box-shadow:0 6px 18px rgba(0,0,0,.06);
}

/* BUTTON */
.btn-accent {
	background:#2563eb;
	color:white;
	border-radius:999px;
	padding:.5rem 1.5rem;
}
.btn-accent:hover {
	background:#1e40af;
}
</style>

</head>

<body>

<nav class="navbar navbar-expand-lg bg-white shadow-sm px-4">
<a class="navbar-brand" href="{{ url_for('home') }}">
    <img src="https://cdn-icons-png.flaticon.com/512/2966/2966486.png"
         alt="SmileCare Logo"
         class="navbar-logo"
         style="height:40px; object-fit:contain; margin-right:10px;">
    SmileCare Dental
</a>
	<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">
		<span class="navbar-toggler-icon"></span>
	</button>

	<div id="nav" class="collapse navbar-collapse">
		<ul class="navbar-nav ms-auto gap-3">
			<li class="nav-item"><a class="nav-link" href="#services">Services</a></li>
			<li class="nav-item"><a class="nav-link" href="#dentists">Dentists</a></li>
			<li class="nav-item"><a class="nav-link" href="#testimonials">Testimonials</a></li>
			<li class="nav-item">
				<a class="btn btn-accent" href="{{ url_for('index') }}">Book Appointment</a>
			</li>
		</ul>
	</div>
</nav>



<div class="container-narrow my-4">
	{{ content | safe }}
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# Register and Log-in
@APP.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        name = request.form.get("name","").strip()
        email = request.form.get("email","").strip()
        password = request.form.get("password","").strip()
        if not (name and email and password):
            flash("Fill all fields", "warning")
            return redirect(url_for("register"))
        try:
            register_user(name,email,password)
            flash("Registration successful! Login now.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already exists", "danger")
            return redirect(url_for("register"))
    content = render_template_string("""
<h2>Register</h2>
<form method="post">
<div class="mb-2"><input class="form-control" name="name" placeholder="Name" required></div>
<div class="mb-2"><input class="form-control" name="email" placeholder="Email" type="email" required></div>
<div class="mb-2"><input class="form-control" name="password" placeholder="Password" type="password" required></div>
<button class="btn btn-accent w-100">Register</button>
<p class="mt-2">Already have an account? <a href="{{ url_for('login') }}">Login</a></p>
</form>
""")
    return render_template_string(BASE_TEMPLATE, content=content)

@APP.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        email = request.form.get("email","").strip()
        password = request.form.get("password","").strip()
        user = login_user(email,password)
        if user:
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            flash(f"Welcome {user[1]}!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for("login"))
    content = render_template_string("""
<h2>Login</h2>
<form method="post">
<div class="mb-2"><input class="form-control" name="email" placeholder="Email" type="email" required></div>
<div class="mb-2"><input class="form-control" name="password" placeholder="Password" type="password" required></div>
<button class="btn btn-accent w-100">Login</button>
<p class="mt-2">Don't have an account? <a href="{{ url_for('register') }}">Register</a></p>
</form>
""")
    return render_template_string(BASE_TEMPLATE, content=content)

@APP.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for("home"))

# Routes
@APP.route("/book", methods=["GET", "POST"])
def index():
		dentists = get_dentists()
		if request.method == "POST":
				name = request.form.get("patient_name","").strip()
				age = request.form.get("age","").strip()
				contact = request.form.get("contact","").strip()
				dentist_id = request.form.get("dentist","").strip()
				service = request.form.get("service","").strip()
				date = request.form.get("date","").strip()
				time_slot = request.form.get("time","").strip()

				if not (name and age and contact and dentist_id and service and date and time_slot):
						flash("Please fill all fields", "warning")
						return redirect(url_for("index"))

				existing = find_patient_by_name(name)
				if existing:
						pid = existing[0]
				else:
						pid = add_patient(name, age, contact)

				add_appointment(pid, dentist_id, service, date, time_slot)
				flash("Appointment added — pending approval", "success")
				return redirect(url_for("index"))

		content = render_template_string("""
<div class="row g-4 align-items-start">
	<div class="col-lg-4">
		<div class="card p-4">
			<h5 class="section-title">Book Appointment</h5>
			<form method="get" action="{{ url_for('index') }}">
				<div class="mb-2">
					<label class="form-label">Patient Name</label>
					<input class="form-control" name="patient_name" required>
				</div>
				<div class="row">
					<div class="col"><label class="form-label">Age</label><input class="form-control" name="age" required></div>
					<div class="col"><label class="form-label">Contact</label><input class="form-control" name="contact" required></div>
				</div>
				<div class="mt-2">
					<label class="form-label">Dentist</label>
					<select name="dentist" class="form-select" required>
						<option value="">Select dentist</option>
						{% for d in dentists %}
							<option value="{{ d[0] }}">{{ d[1] }} ({{ d[2] }})</option>
						{% endfor %}
					</select>
				</div>
				<div class="mt-2">
					<label class="form-label">Service</label>
					<select id="service_select" class="form-select mb-2">
						<option value="">Choose service</option>
						<option>Cleaning</option>
						<option>Check-up</option>
						<option>Tooth Extraction</option>
						<option>Braces Adjustment</option>
						<option>Root Canal</option>
						<option>Whitening</option>
					</select>
					<input id="service_custom" name="service" class="form-control" placeholder="Or enter custom service">
				</div>
				<div class="row mt-2">
					<div class="col"><label class="form-label">Date</label><input type="date" class="form-control" name="date" required></div>
					<div class="col"><label class="form-label">Time</label>
						<select name="time" class="form-select" required>
							<option value="">Select</option>
							{% for t in time_slots %}
								<option value="{{ t }}">{{ t }}</option>
							{% endfor %}
						</select>
					</div>
				</div>
				<button class="btn btn-accent w-100 mt-3">Book Appointment</button>
			</form>
			<p class="muted small mt-2 text-center">Clinic Hours: 08:00 AM – 06:00 PM</p>
		</div>
	</div>

	<div class="col-lg-8">
		<div class="card p-4">
			<h5 class="section-title">Upcoming Appointments</h5>
			<div class="table-responsive">
				<table class="table align-middle">
					<thead class="table-light">
						<tr><th>Patient</th><th>Service</th><th>Date</th><th>Time</th><th>Dentist</th><th>Status</th></tr>
					</thead>
					<tbody>
						{% for r in rows %}
						<tr>
							<td>{{ r[1] }}</td>
							<td>{{ r[4] }}</td>
							<td>{{ r[5] }}</td>
							<td>{{ r[6] }}</td>
							<td>{{ r[7] }} ({{ r[8] }})</td>
							<td><span class="badge bg-secondary">{{ r[9] }}</span></td>
						</tr>
						{% else %}
						<tr><td colspan="6" class="text-center muted">No appointments yet</td></tr>
						{% endfor %}
					</tbody>
				</table>
			</div>
		</div>
	</div>
</div>

<script>
const dropdown = document.getElementById('service_select');
const customBox = document.getElementById('service_custom');
dropdown.addEventListener('change', () => {
	if (!customBox.value) customBox.value = dropdown.value;
});
</script>
""", dentists=dentists, time_slots=TIME_SLOTS, rows=get_appointments())
		return render_template_string(BASE_TEMPLATE, content=content)

# Moderator Route
@APP.route("/moderator", methods=["GET", "POST"])
def moderator():
		search_query = request.args.get("q","")
		rows = get_appointments(search_query)
		dentists = get_dentists()
		content = render_template_string("""
<div class="d-flex justify-content-between align-items-center mb-3">
	<h3>Moderator Dashboard</h3>
	<div>
		<a class="btn btn-outline-primary me-2" href="{{ url_for('index') }}">Home</a>
		<button class="btn btn-accent" data-bs-toggle="modal" data-bs-target="#manageDentistsModal">Manage Dentists</button>
	</div>
</div>

<form class="mb-3" method="get" action="{{ url_for('moderator') }}">
	<div class="input-group">
		<input class="form-control" type="text" name="q" placeholder="Search patient/dentist/service" value="{{ request.args.get('q','') }}">
		<button class="btn btn-primary" type="submit">Search</button>
	</div>
</form>

<div class="card p-3">
	<div class="table-responsive">
		<table class="table table-striped">
			<thead><tr>
				<th>Patient</th><th>Age</th><th>Contact</th><th>Service</th><th>Date</th><th>Time</th><th>Dentist</th><th>Status</th><th>Actions</th>
			</tr></thead>
			<tbody>
				{% for r in rows %}
				<tr>
					<td>{{ r[1] }}</td><td>{{ r[2] }}</td><td>{{ r[3] }}</td><td>{{ r[4] }}</td>
					<td>{{ r[5] }}</td><td>{{ r[6] }}</td><td>{{ r[7] }} ({{ r[8] }})</td><td>{{ r[9] }}</td>
					<td>
						<div class="btn-group btn-group-sm">
							<a class="btn btn-sm btn-success" href="{{ url_for('action', aid=r[0], status='approved') }}">Approve</a>
							<a class="btn btn-sm btn-info" href="{{ url_for('action', aid=r[0], status='completed') }}">Complete</a>
							<a class="btn btn-sm btn-warning" href="{{ url_for('action', aid=r[0], status='cancelled') }}">Cancel</a>
							<a class="btn btn-sm btn-danger" href="{{ url_for('delete', aid=r[0]) }}" onclick="return confirm('Delete appointment?')">Delete</a>
						</div>
					</td>
				</tr>
				{% else %}
				<tr><td colspan="9" class="text-center muted">No appointments</td></tr>
				{% endfor %}
			</tbody>
		</table>
	</div>
</div>

<!-- Manage Dentists Modal -->
<div class="modal fade" id="manageDentistsModal" tabindex="-1">
	<div class="modal-dialog modal-md">
		<div class="modal-content">
			<div class="modal-header">
				<h5 class="modal-title">Manage Dentists</h5>
				<button type="button" class="btn-close" data-bs-dismiss="modal"></button>
			</div>
			<div class="modal-body">
				<div class="mb-3">
					<label class="form-label">Add Dentist</label>
					<div class="input-group">
						<input id="dentistName" class="form-control" placeholder="Dentist name">
						<input id="dentistSpecialty" class="form-control" placeholder="Specialty">
						<button class="btn btn-primary" onclick="addDentist()">Add</button>
					</div>
				</div>
				<div>
					<label class="form-label">Existing Dentists</label>
					<ul id="dentistList" class="list-group">
						{% for d in dentists %}
							<li class="list-group-item d-flex justify-content-between align-items-center">
								{{ d[1] }} ({{ d[2] }})
								<button class="btn btn-sm btn-danger" onclick="deleteDentist('{{ d[0] }}')">Delete</button>
							</li>
						{% else %}
							<li class="list-group-item text-muted">No dentists yet</li>
						{% endfor %}
					</ul>
				</div>
			</div>
			<div class="modal-footer"><button class="btn btn-secondary" data-bs-dismiss="modal">Close</button></div>
		</div>
	</div>
</div>

<script>
async function addDentist(){
		const name = document.getElementById('dentistName').value.trim();
		const specialty = document.getElementById('dentistSpecialty').value.trim() || "General";
		if(!name){ alert('Enter dentist name'); return; }
		const res = await fetch('{{ url_for('api_add_dentist') }}', {
			method:'POST', headers: {'Content-Type':'application/json'},
			body: JSON.stringify({ name, specialty })
		});
		const j = await res.json();
		if(j.success) location.reload();
		else alert('Error: ' + j.error);
}
async function deleteDentist(id){
		if(!confirm('Delete dentist?')) return;
		const res = await fetch('{{ url_for('api_delete_dentist') }}', {
			method:'POST', headers: {'Content-Type':'application/json'},
			body: JSON.stringify({ id })
		});
		const j = await res.json();
		if(j.success) location.reload();
		else alert('Error: ' + j.error);
}
</script>
""", rows=rows, dentists=dentists)
		return render_template_string(BASE_TEMPLATE, content=content)

# Route 

@APP.route("/", methods=["GET"])
def home():
	content = render_template_string("""
<div class="container-narrow">

<!-- HERO -->
<div class="hero mb-5">
	<div class="row align-items-center">
		<div class="col-md-7">
			<h1 class="fw-bold">Your Smile, Our Priority</h1>
			<p class="lead mt-2">
				Professional dental care with expert dentists and modern facilities.
			</p>
			<a href="{{ url_for('index') }}" class="btn btn-light btn-lg mt-3">Book Appointment</a>
		</div>
		<div class="col-md-5 d-none d-md-block text-end">
			<img src="https://images.unsplash.com/photo-1606811841689-23dfddce3e95"
			     class="section-img" style="max-height:260px;">
		</div>
	</div>
</div>

<!-- SERVICES -->
<div id="services" class="section section-white">
	<h2 class="text-center mb-4">Our Services</h2>
	<div class="row g-4">
		<div class="col-md-4">
			<div class="service-card">
				<img src="https://images.unsplash.com/photo-1588776814546-1ffcf47267a5" class="section-img mb-3">
				<h5>Dental Cleaning</h5>
				<p class="text-muted">Professional cleaning for healthier teeth and gums.</p>
			</div>
		</div>
		<div class="col-md-4">
			<div class="service-card">
				<img src="https://images.unsplash.com/photo-1629909613654-28e377c37b09" class="section-img mb-3">
				<h5>Expert Dentists</h5>
				<p class="text-muted">Experienced and licensed dental professionals.</p>
			</div>
		</div>
		<div class="col-md-4">
			<div class="service-card">
				<img src="https://upload.wikimedia.org/wikipedia/commons/d/d9/Dental_Chair_UMSOD.jpg" class="section-img mb-3">
				<h5>Modern Equipment</h5>
				<p class="text-muted">State-of-the-art technology for safe treatments.</p>
			</div>
		</div>
	</div>
</div>

<!-- DENTISTS -->
								  
<div id="dentists" class="section section-light">
	<div class="row align-items-center g-10">
		<div class="col-md-6">
			<h2>Meet Our Dentists</h2>
			<p class="text-muted">
				Our dentists specialize in preventive, cosmetic, and restorative dentistry.
			</p>
		</div>
		<div class="col-md-6">
			<img src="https://t3.ftcdn.net/jpg/02/77/60/02/360_F_277600288_daUMNqpwmR1zZJs3SWsEWVo6csA9SDev.jpg" class="section-img">
								  
		</div>
	</div>
</div>

<!-- TESTIMONIALS -->
<div id="testimonials" class="section section-white">
	<h2 class="text-center mb-4">What Our Patients Say</h2>
	<div class="row g-4">
		<div class="col-md-4">
			<div class="testimonial">
				<p>"Very clean clinic and friendly staff. Highly recommended!"</p>
				<strong>— Maria L.</strong>
			</div>
		</div>
		<div class="col-md-4">
			<div class="testimonial">
				<p>"The dentists explained everything clearly. No pain at all."</p>
				<strong>— John D.</strong>
			</div>
		</div>
		<div class="col-md-4">
			<div class="testimonial">
				<p>"Booking an appointment was fast and easy."</p>
				<strong>— Anne C.</strong>
			</div>
		</div>
	</div>
</div>

<!-- CTA -->
<div class="section section-light text-center">
	<h3 class="fw-bold mb-3">Ready for a Brighter Smile?</h3>
	<a href="{{ url_for('index') }}" class="btn btn-accent btn-lg">Book Appointment</a>
</div>

</div>
""")
	return render_template_string(BASE_TEMPLATE, content=content)




@APP.route("/action/<aid>/<status>")
def action(aid, status):
		update_appointment_status(aid, status)
		flash("Status updated", "success")
		return redirect(url_for("moderator"))

@APP.route("/delete/<aid>")
def delete(aid):
		delete_appointment(aid)
		flash("Appointment deleted", "info")
		return redirect(url_for("moderator"))

# Dentist API
@APP.route("/api/dentist/add", methods=["POST"])
def api_add_dentist():
		data = request.get_json() or {}
		name = data.get("name","").strip()
		specialty = data.get("specialty","General").strip()
		if not name: return jsonify(success=False, error="Missing name")
		try:
				add_dentist(name, specialty)
				return jsonify(success=True)
		except Exception as e:
				return jsonify(success=False, error=str(e))

@APP.route("/api/dentist/delete", methods=["POST"])
def api_delete_dentist():
		data = request.get_json() or {}
		did = data.get("id")
		if not did: return jsonify(success=False, error="Missing id")
		try:
				delete_dentist_by_id(did)
				return jsonify(success=True)
		except Exception as e:
				return jsonify(success=False, error=str(e))

# Main
if __name__ == "__main__":
		init_db()
		APP.run(debug=True)
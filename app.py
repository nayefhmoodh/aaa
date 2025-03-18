from flask import Flask, render_template, request, redirect, session, url_for
import requests

app = Flask(__name__)
app.secret_key = "supersecret"

API_URL = "https://leakcheck.io/api/v2/query/"
API_KEY = "555519853738a6859ba109ce657c0757768c6497"
HEADERS = {
    "Accept": "application/json",
    "X-Api-Key": API_KEY,
}

def fetch_breach_data(domain):
    response = requests.get(f"{API_URL}{domain}?type=domain", headers=HEADERS)
    if response.status_code != 200:
        return {"error": "فشل في جلب البيانات"}
    
    data = response.json()
    if not data.get("success"):
        return {"error": "لم يتم العثور على بيانات"}
    
    return [
        {
            "email": entry.get("email"),
            "password": entry.get("password"),
            "origin": entry.get("origin", [])
        }
        for entry in data.get("result", [])
        if entry.get("source", {}).get("name") == "Stealer Logs"
    ]

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == "admin" and password == "Nayef@1512":
            session['user'] = username
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="بيانات تسجيل الدخول غير صحيحة!")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/breach', methods=['GET'])
def breach_results():
    if 'user' not in session:
        return redirect(url_for('login'))
    domain = request.args.get('domain')
    if not domain:
        return redirect(url_for('dashboard'))
    data = fetch_breach_data(domain)
    return render_template('results.html', domain=domain, results=data)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

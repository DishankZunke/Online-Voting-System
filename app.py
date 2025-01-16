from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'securekey'  # For session handling


users_db = {}
candidates = {
    'John Doe': {'politician': 'Politician A', 'votes': 0},
    'Jane Smith': {'politician': 'Politician B', 'votes': 0},
    'Alice Johnson': {'politician': 'Politician C', 'votes': 0}
}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form['user_id']
        username = request.form['username']
        age = request.form['age']

        if user_id in users_db:
            flash("User ID already exists. Please choose a different ID.", "error")
            return redirect(url_for('register'))
        
        if not age.isdigit() or int(age) < 18:
            flash("Invalid age or below voting age (18+).", "error")
            return redirect(url_for('register'))

        # Register user
        users_db[user_id] = {
            'username': username,
            'age': int(age),
            'has_voted': False
        }
        flash("Registration successful! Please log in now.", "success")
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        if user_id in users_db:
            session['user_id'] = user_id
            flash(f"Welcome {users_db[user_id]['username']}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid user ID.", "error")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = users_db[user_id]
    return render_template('dashboard.html', user=user)

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'user_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = users_db[user_id]

    if user['has_voted']:
        flash("You have already voted!", "error")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        choice = request.form['candidate']
        if choice in candidates:
            candidates[choice]['votes'] += 1
            user['has_voted'] = True
            flash(f"Your vote for {choice} has been casted. Thank you!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid candidate selection.", "error")
    
    return render_template('vote.html', candidates=candidates)

@app.route('/results')
def results():
    if not candidates:
        flash("No candidates available for voting.", "error")
        return redirect(url_for('dashboard'))

    # Find the candidate(s) with the maximum votes
    max_votes = max(candidate['votes'] for candidate in candidates.values())
    winners = [name for name, details in candidates.items() if details['votes'] == max_votes]

    return render_template('results.html', candidates=candidates, winners=winners, max_votes=max_votes)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

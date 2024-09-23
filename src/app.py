from flask import Flask, request, render_template, redirect, url_for, flash
from datetime import datetime
from web3 import Web3, HTTPProvider
import json

app = Flask(__name__)
app.secret_key = 'secret-key-for-flash-messages'  # Needed for flashing messages
blockchain = 'http://127.0.0.1:7545'

# Connect to Ethereum blockchain and Voting contract
def connect():
    web3 = Web3(HTTPProvider(blockchain))
    if not web3.isConnected():
        raise Exception("Could not connect to Ethereum network")
    web3.eth.defaultAccount = web3.eth.accounts[0]
    artifact_path = "../build/contracts/Voting.json"  # Adjust the path as needed
    with open(artifact_path) as f:
        artifact_json = json.load(f)
        contract_abi = artifact_json['abi']
        contract_address = artifact_json['networks']['5777']['address']
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    return contract, web3

contract, web3 = connect()

# Mock data for candidates and voters
candidates = {}
voters = {}
count_candidates = 0
voting_start = None
voting_end = None

# Home page - shows available candidates and voting option
@app.route('/')
def home():
    return render_template('index.html', candidates=candidates)

# Admin page for adding candidates and setting voting dates
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    global count_candidates, voting_start, voting_end

    if request.method == 'POST':
        if 'add_candidate' in request.form:
            # Adding a candidate
            name = request.form.get('name')
            party = request.form.get('party')
            count_candidates += 1
            candidates[count_candidates] = {'id': count_candidates, 'name': name, 'party': party, 'vote_count': 0}
            flash(f"Candidate '{name}' added successfully!", 'success')
        elif 'set_dates' in request.form:
            # Setting voting dates
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            voting_start = datetime.strptime(start_date, '%Y-%m-%d').timestamp()
            voting_end = datetime.strptime(end_date, '%Y-%m-%d').timestamp()
            if voting_end <= voting_start:
                flash("End date must be after start date.", 'danger')
            else:
                flash(f"Voting dates set from {start_date} to {end_date}.", 'success')
    
    return render_template('admin.html', candidates=candidates, voting_start=voting_start, voting_end=voting_end)

# Voting page for submitting a vote
@app.route('/vote', methods=['POST'])
def vote():
    global voting_start, voting_end

    candidate_id = int(request.form.get('candidate_id'))
    voter_address = request.form.get('voter_address')

    # Check if voting is active
    now = datetime.now().timestamp()
    if voting_start is None or voting_end is None:
        flash("Voting dates have not been set.", 'danger')
        return redirect(url_for('home'))  # Ensure this redirects to the correct page

    if not (voting_start <= now <= voting_end):
        flash("Voting is not active.", 'danger')
        return redirect(url_for('home'))

    # Check if voter has already voted
    if voter_address in voters:
        flash("You have already voted.", 'danger')
        return redirect(url_for('home'))

    # Check if candidate exists
    if candidate_id <= 0 or candidate_id > count_candidates:
        flash("Invalid candidate selection.", 'danger')
        return redirect(url_for('home'))

    # Record the vote
    voters[voter_address] = True
    candidates[candidate_id]['vote_count'] += 1

    # Record the vote on the Ethereum blockchain
    try:
        tx_hash = contract.functions.vote(candidate_id).transact({'from': voter_address})
        flash(f"Vote recorded successfully! Transaction hash: {tx_hash.hex()}", 'success')
    except Exception as e:
        flash(f"Transaction failed: {str(e)}", 'danger')

    return redirect(url_for('home'))  # Ensure this redirects to the correct page

# Login page for admin
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'password':
            return redirect(url_for('admin'))
        else:
            flash('Invalid login credentials', 'danger')
    return render_template('login.html')

# Run the Flask application
if __name__ == '__main__':
    app.run(port=4000, debug=True)
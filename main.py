import json
import os
from flask import Flask, render_template, redirect, request, session
import datetime as dt
from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from YamahaFirmware import YamahaFirmware  # Assuming this import is correct
import os
import time
os.environ['TZ'] = 'Europe/Brussels'

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for session management

# File paths
JSON_FILE = 'firmware_info.json'
VISITORS_FILE = 'visitors_count.json'
DOWNLOADS_FILE = 'downloads_count.json'

# Global variable to store last refreshed time
last_refreshed = ""

# Load firmware information from the JSON file
def load_firmware_info_from_file():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r') as file:
            return json.load(file)
    return []

# Save firmware information to the JSON file
def save_firmware_info_to_file(data):
    with open(JSON_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# Load the visitors count
def load_visitors_count():
    if os.path.exists(VISITORS_FILE):
        with open(VISITORS_FILE, 'r') as file:
            return json.load(file)
    return 0

# Save the visitors count
def save_visitors_count(count):
    with open(VISITORS_FILE, 'w') as file:
        json.dump(count, file)

# Load download counts for each device
def load_downloads_count():
    if os.path.exists(DOWNLOADS_FILE):
        with open(DOWNLOADS_FILE, 'r') as file:
            return json.load(file)
    return {}

# Save download counts
def save_downloads_count(counts):
    with open(DOWNLOADS_FILE, 'w') as file:
        json.dump(counts, file)

# Fetch firmware information (simulate fetching data, assuming YamahaFirmware is a real module)
def fetch_firmware_info():
    firmware = YamahaFirmware.get_info_all(return_json=False)
    name_list = []
    version_list = []
    links_list = []

    for item in firmware:
        name_list.append(item[0])
        version_list.append(item[1])
        links_list.append(item[2])

    combined_data = list(zip(name_list, version_list, links_list))
    return combined_data

# Refresh firmware info and save it to the file
def refresh():
    global last_refreshed
    last_refreshed = datetime.now(timezone.utc).isoformat()  # "YYYY-MM-DDTHH:MM:SSZ"
    data = fetch_firmware_info()
    save_firmware_info_to_file(data)
    print(f"data refreshed at {datetime.now()}")

# Initialize scheduler to refresh data every 3 hours
scheduler = BackgroundScheduler()
scheduler.add_job(func=refresh, trigger="interval", hours=3, next_run_time=(datetime.now() + dt.timedelta(seconds=5)))
scheduler.start()

@app.before_request
def track_unique_visits():
    """Track unique visits by using sessions."""
    if 'has_visited' not in session:
        session['has_visited'] = True
        visitors_count = load_visitors_count()
        visitors_count += 1
        save_visitors_count(visitors_count)

@app.route('/')
def home():
    """Main page to display firmware data."""
    data = load_firmware_info_from_file()
    visitors_count = load_visitors_count()
    downloads_count = load_downloads_count()
    return render_template('firmware_info.html', data=data, last_refreshed=last_refreshed, visitors_count=visitors_count, downloads_count=downloads_count)

@app.route('/manualrefresh')
def manual_refresh():
    """Trigger a manual refresh."""
    refresh()  # Call the refresh function
    time.sleep(10)  # import time
    return redirect("/")

@app.route('/download/<device>', methods=['GET'])
def download(device):
    """Track download clicks and redirect to the actual download link."""
    downloads_count = load_downloads_count()
    if device in downloads_count:
        downloads_count[device] += 1
    else:
        downloads_count[device] = 1
    save_downloads_count(downloads_count)

    # Find the download link for the device
    download_link = next(item[2] for item in load_firmware_info_from_file() if item[0] == device)
    return redirect(download_link)

# Run the Flask app
if __name__ == '__main__':
    try:
        app.run(debug=True, use_reloader=False, port=5003, host="0.0.0.0")
    except (KeyboardInterrupt, SystemExit):
        # Shutdown the scheduler gracefully on exit
        scheduler.shutdown()

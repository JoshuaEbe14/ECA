# https://medium.com/@dmitryrastorguev/basic-user-authentication-login-for-flask-using-mongoengine-and-wtforms-922e64ef87fe

from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, jsonify, url_for, redirect
from app import app, db #, login_manager

from werkzeug.security import generate_password_hash

# Register Blueprint so we can factor routes
# from bmi import bmi, get_dict_from_csv, insert_reading_data_into_database

from controllers.dashboard import dashboard
from controllers.auth import auth
from controllers.bookController import booking
from controllers.packageController import package

from models.package import Package
from models.book import Booking
from models.users import User
from models.forms import BookForm

#for uploading file
import csv
import io
import json
import datetime as dt
import os

# register blueprint from respective module
app.register_blueprint(dashboard)
app.register_blueprint(auth)
app.register_blueprint(booking)
app.register_blueprint(package)

@app.template_filter('formatdate') # use this name
def format_date(value, format="%d/%m/%Y"):
    if value is None:
        return ""
    try:
        return value.strftime(format)
    except Exception:
        # Replaces Windows-specific '#'-modifiers with POSIX '-' and try again
        try:
            fmt = format.replace("%#d", "%-d").replace("%#m", "%-m")
            return value.strftime(fmt)
        except Exception:
            # Final fallback that's fully portable
            return f"{value.day}/{value.month:02d}/{value.year}"

@app.template_filter('formatmoney') # use this name
def format_money(value, ndigits=2):
    """Format money with 2 decimal digits"""
    if value is None:
        return ""
    return f'{value:.{ndigits}f}'

@app.route('/base')
def show_base():
    return render_template('base.html')

@app.route("/upload", methods=['GET','POST'])
@login_required
def upload():
    if request.method == 'GET':
        return render_template("upload.html", name=current_user.name, panel="Upload")
    elif request.method == 'POST':
        type = request.form.get('type')
        if type == 'create':
            print("No create Action yet")
        elif type == 'upload':
            file = request.files.get('file')
            datatype = request.form.get('datatype')

            data = file.read().decode('utf-8')
            dict_reader = csv.DictReader(io.StringIO(data), delimiter=',', quotechar='"')
            file.close()

            if datatype == "Users":
                for item in list(dict_reader):
                    pwd = generate_password_hash(item['password'], method='sha256')
                    User.createUser(email=item['email'], password=pwd, name=item['name'])
            elif datatype == "Package":
                for item in list(dict_reader):
                    Package.createPackage(hotel_name=item['hotel_name'], duration=int(item['duration']),
                        unit_cost=float(item['unit_cost']), image_url=item['image_url'],
                        description=item['description'])
            elif datatype == "Booking":
                for item in list(dict_reader):
                    existing_user = User.getUser(email=item['customer'])
                    existing_package = Package.getPackage(hotel_name=item['hotel_name'])
                    try:
                        check_in_date=dt.datetime.strptime(item['check_in_date'], "%Y-%m-%d")
                    except Exception:
                        # Skip bad date format rather than creating invalid record
                        print(f"Skipping booking row with invalid date: {item['check_in_date']}")
                        continue
                    if not existing_user or not existing_package:
                        print(f"Skipping booking row due to missing user/package: user={existing_user} package={existing_package}")
                        continue
                    aBooking = Booking.createBooking(check_in_date=check_in_date, customer=existing_user, package=existing_package)
                    aBooking.calculate_total_cost()
            elif datatype == "ListOfBooking":
                # CSV columns: check_in_date, customer, hotel_names (JSON array string)
                # For each row, create sequential bookings across the list of hotels starting at check_in_date
                for item in list(dict_reader):
                    raw_date = item.get('check_in_date', '').strip()
                    # Try multiple date formats
                    check_in_date = None
                    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
                        try:
                            check_in_date = dt.datetime.strptime(raw_date, fmt)
                            break
                        except Exception:
                            continue
                    if not check_in_date:
                        print(f"Invalid date format in row: {raw_date}")
                        continue

                    email = item.get('customer', '').strip()
                    customer = User.getUser(email=email)
                    if not customer:
                        print(f"Unknown user, skipping row: {email}")
                        continue

                    hotels_raw = item.get('hotel_names', '').strip()
                    try:
                        hotels = json.loads(hotels_raw.replace("'", '"'))
                    except Exception:
                        hotels = [h.strip().strip('"').strip("'") for h in hotels_raw.split(',') if h.strip()]

                    current_date = check_in_date
                    for hotel in hotels:
                        package = Package.getPackage(hotel_name=hotel)
                        if not package:
                            print(f"Package not found, skipping hotel: {hotel}")
                            continue
                        Booking.createBooking(check_in_date=current_date, customer=customer, package=package)
                        # advance by duration nights
                        current_date = current_date + dt.timedelta(days=package.duration)
                    
        return render_template("upload.html", panel="Upload")
    
@app.route("/changeAvatar")
def changeAvatar():
    basedir = os.path.abspath(os.path.dirname(__file__))
    # Specify the relative path to the subfolder
    subfolder_path = os.path.join('assets', 'img/avatar')
    # Join the base directory with the subfolder path
    subfolder_abs_path = os.path.join(basedir, subfolder_path)
    
    files = []
    for filename in os.listdir(subfolder_abs_path):
        path = os.path.join(subfolder_abs_path, filename)
        if os.path.isfile(path):
            files.append(filename)
            # url_for('static') /static/default.jpg etc
    return render_template("changeAvatar.html", filenames=files, panel="Change Avatar") 

@app.route("/chooseAvatar", methods=['POST'])
def chooseAvatar():
    # get the filename
    chosenPath = request.json['path']
    print('chosen path: ', chosenPath)
  
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Specify the relative path to the subfolder
    subfolder_path = os.path.join('assets', 'img/avatar')

    # Join the base directory with the subfolder path
    subfolder_abs_path = os.path.join(basedir, subfolder_path)
    
    filename = chosenPath.split('/')[-1]
    User.addAvatar(current_user, filename)
    
    return jsonify(path=chosenPath)

  
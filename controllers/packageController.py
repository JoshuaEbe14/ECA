from flask_login import login_user, login_required, logout_user, current_user
from flask import Blueprint, request, redirect, render_template, url_for

from models.forms import BookForm

from models.users import User
from models.package import Package

package = Blueprint('packageController', __name__)

@package.route('/')
@package.route('/packages')
def packages():
    all_packages = Package.getAllPackages()
    return render_template('packages.html', panel="Package", all_packages=all_packages)

@package.route("/viewPackageDetail/<hotel_name>")
def viewPackageDetail(hotel_name):
    the_package = Package.getPackage(hotel_name=hotel_name)
    return render_template('packageDetail.html', panel="Package Detail", package=the_package)

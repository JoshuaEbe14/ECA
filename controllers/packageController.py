from flask_login import login_user, login_required, logout_user, current_user
from flask import Blueprint, request, redirect, render_template, url_for, flash
from markupsafe import Markup

from models.forms import BookForm

from models.users import User
from models.package import Package
from models.bundle import BundlePurchase

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

@package.route('/bundlePurchase', methods=['POST'])
@login_required
def bundlePurchase():
    selected = request.form.getlist('bundle_packages')
    if not selected:
        flash('Please select packages to buy as a bundle')
        return redirect(url_for('packageController.packages'))

    # Retrieve package objects, ignore invalid names
    packages = [Package.getPackage(hotel_name=h) for h in selected]
    packages = [p for p in packages if p]
    if not packages:
        flash('Selected packages not found.')
        return redirect(url_for('packageController.packages'))

    # Persist bundle purchase (unlimited per day, purchased_date auto set)
    BundlePurchase.create(customer=current_user, packages=packages)

    # Pricing + Discount messaging (retain existing logic: discount only when >=2)
    total = sum(p.unit_cost * p.duration for p in packages)
    if len(packages) == 1:
        msg = f'Bundle (single) purchased: {packages[0].hotel_name}. Total cost ${total:,.2f}. Utilised flags set to false.'
    else:
        discount_rate = 0.10
        discounted_total = total * (1 - discount_rate)
        msg = (
            f'Bundle purchased with {len(packages)} packages.<br>'
            f'Original ${total:,.2f}. Discounted total ${discounted_total:,.2f}.<br>'
            'All utilised flags set to false.'
        )
    flash(Markup(msg))
    return redirect(url_for('packageController.packages'))

@package.route('/myBundles')
@login_required
def myBundles():
    """List bundles purchased by current user."""
    bundles = BundlePurchase.getByUser(current_user)
    return render_template('packages.html', panel="My Bundle Purchases", all_packages=Package.getAllPackages(), bundles=bundles)

from flask_login import login_user, login_required, logout_user, current_user
from flask import Blueprint, request, redirect, render_template, url_for, flash
from markupsafe import Markup

from models.forms import BookForm

from models.users import User
from models.package import Package
from models.bundle import BundlePurchase
import datetime as dt

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
    package_names = ", ".join(p.hotel_name for p in packages)

    count = len(packages)
    # Determine discount tier
    if count == 1:
        discount_rate = 0.0
    elif 2 <= count <= 3:
        discount_rate = 0.10
    else:  # 4 or more
        discount_rate = 0.20

    discounted_total = total * (1 - discount_rate)

    if discount_rate == 0:
        msg = (
            f'No discount for bundle purchase for {package_names}.<br>'
            f'Total cost ${total:,.2f}'
        )
    else:
        msg = (
            f'{int(discount_rate*100)}% discount for bundle purchase for {package_names}.<br>'
            f'Total cost: ${total:,.2f}<br>'
            f'Discounted total ${discounted_total:,.2f}'
        )
    flash(Markup(msg))
    return redirect(url_for('packageController.packages'))

@package.route('/myBundles')
@login_required
def myBundles():
    """List bundles purchased by current user."""
    bundles = BundlePurchase.getByUser(current_user).order_by('purchased_date')
    return render_template('packages.html', panel="My Bundle Purchases", all_packages=Package.getAllPackages(), bundles=bundles)

@package.route('/manageBundle')
@login_required
def manageBundle():
    """Manage Bundle function for non-admin users.

    - Shows bundles purchased by the current user sorted by ascending purchased date
    - Allows making a booking by choosing a check-in date per bundled package
    - If no purchased bundles, shows the empty-state message in the template
    """
    # Restrict to non-admin users (assignment requirement mirrors other non-admin functions)
    if getattr(current_user, 'name', '') == 'Admin':
        flash('This is a non-admin function. Please log in as a non-admin user to use this function.')
        return redirect(url_for('packageController.packages'))

    bundles = BundlePurchase.getByUser(current_user).order_by('purchased_date')
    # Prepare enriched bundle data for template (expiry logic handled in model helpers, but we expose stamp)
    enriched = []
    for b in bundles:
        enriched.append({
            'obj': b,
            'purchase_date': b.purchased_date,
            'expiry_date': b.expiry_date,
            'expired': b.is_expired,
            'packages': b.bundledPackages
        })
    return render_template('manageBundle.html', panel='Manage Bundles', bundles=enriched)

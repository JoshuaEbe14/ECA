from app import db
from models.users import User
from models.package import Package
import datetime as dt


class BundledPackage(db.EmbeddedDocument):
    """An item within a bundle purchase.

    Fields
    - package: Reference to a Package
    - utilised: Whether this package has been used or redeemed
    """
    package = db.ReferenceField(Package, required=True)
    utilised = db.BooleanField(default=False)


class BundlePurchase(db.Document):
    """Represents a bundle of one or more packages purchased by a user.

    Business rules (extended):
    - A bundle expires one year after its purchased_date.
    - Packages must be booked before expiry; otherwise they are considered expired.
    - Once an embedded package is booked we mark it utilised=True.
    """

    meta = {"collection": "bundlePurchases"}

    purchased_date = db.DateTimeField(required=True, default=lambda: dt.datetime.utcnow())
    customer = db.ReferenceField(User, required=True)
    bundledPackages = db.ListField(db.EmbeddedDocumentField(BundledPackage))

    @staticmethod
    def create(customer: User, packages: list[Package]):
        """Create a bundle purchase for the given user and list of Package objects.

        - purchased_date is set to 'now' (UTC)
        - each bundled package is initialised with utilised=False
        """
        if not customer or not packages:
            raise ValueError("customer and packages are required")
        items = [BundledPackage(package=p, utilised=False) for p in packages]
        bundle = BundlePurchase(customer=customer, bundledPackages=items)
        return bundle.save()

    @staticmethod
    def getByUser(customer: User):
        return BundlePurchase.objects(customer=customer)

    @staticmethod
    def mark_package_utilised(bundle_id, package_id):
        """Mark a specific packaged item in a bundle as utilised.

        Returns the updated document or None if not found.
        """
        bundle: BundlePurchase = BundlePurchase.objects(pk=bundle_id).first()
        if not bundle:
            return None
        for bp in bundle.bundledPackages:
            if str(bp.package.id) == str(package_id):
                bp.utilised = True
        return bundle.save()

    # ---- Expiry helpers ----
    @property
    def expiry_date(self):
        """Expiry is exactly one calendar year (365 days) from purchase."""
        if not self.purchased_date:
            return None
        return self.purchased_date + dt.timedelta(days=365)

    @property
    def is_expired(self):
        exp = self.expiry_date
        if exp is None:
            return False
        # Compare in UTC
        return dt.datetime.utcnow() > exp

    def package_status(self, embedded_pkg: BundledPackage):
        """Return status string for a packaged item based on utilisation and expiry.

        - If bundle expired and not utilised: 'Expired'
        - If utilised: 'Utilised: Yes'
        - Else: 'Un-utilised' (still available to book)
        """
        if embedded_pkg.utilised:
            return 'Utilised: Yes'
        if self.is_expired:
            return 'Expired'
        return 'Un-utilised'

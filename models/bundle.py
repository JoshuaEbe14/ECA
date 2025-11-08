from app import db
from models.users import User
from models.package import Package
import datetime as dt


class BundledPackage(db.EmbeddedDocument):
    """An item within a bundle purchase.

    Fields
    - package: Reference to a Package
    - utilised: Whether this package has been used/redeemed
    """
    package = db.ReferenceField(Package, required=True)
    utilised = db.BooleanField(default=False)


class BundlePurchase(db.Document):
    """Represents a bundle of one or more packages purchased by a user."""

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

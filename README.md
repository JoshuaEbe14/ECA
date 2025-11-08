# Basic User Authentication/Login for Flask using MongoEngine and WTForms

## Introduction

A full description of this project is available as a Medium article [here](https://medium.com/@dmitryrastorguev/basic-user-authentication-login-for-flask-using-mongoengine-and-wtforms-922e64ef87fe).

## Bundle Purchase Feature

This app now supports purchasing one or more staycation packages as a "bundle". Each purchase is stored as a document in MongoDB with this structure:

- collection: `bundlePurchases`
- fields:
	- `purchased_date` (DateTime): when the bundle was bought (set automatically)
	- `customer` (Ref -> `appUsers`): the user who purchased
	- `bundledPackages` (List of Embedded Docs):
		- `package` (Ref -> `staycation`): package included in the bundle
		- `utilised` (Boolean): redemption flag, initialised to `false`

Model classes live in `models/bundle.py`:
- `BundledPackage` (EmbeddedDocument)
- `BundlePurchase` (Document) with helpers:
	- `BundlePurchase.create(customer, packages)`
	- `BundlePurchase.getByUser(customer)`
	- `BundlePurchase.mark_package_utilised(bundle_id, package_id)`

### How to use
1. Go to `/packages` and tick one or more packages.
2. Click "Purchase Bundle" to create a bundle purchase for the current user.
	 - If multiple packages are selected, a 10% discount message is shown (pricing can be adjusted in `controllers/packageController.py`).
3. Optional: visit `/myBundles` to see your bundle history.

### Notes
- There is no limit to the number of bundles that can be purchased in a single day.
- The `utilised` status for each purchased package is set to `false` on creation.
- The purchase date is set to the current timestamp (UTC).


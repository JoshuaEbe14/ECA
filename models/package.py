from app import db

class Package(db.Document):
    meta = {'collection': 'staycation'}
    hotel_name = db.StringField(max_length=30)
    duration = db.IntField()
    unit_cost = db.FloatField()
    image_url = db.StringField(max_length=30)
    description = db.StringField(max_length=500)
    
    def packageCost(self):
        return self.unit_cost * self.duration
    
    @staticmethod
    def getPackage(hotel_name):
        return Package.objects(hotel_name=hotel_name).first()
        
    @staticmethod
    def getAllPackages():
        return Package.objects()
        
    @staticmethod
    def createPackage(hotel_name, duration, unit_cost, image_url, description):
        return Package(hotel_name=hotel_name, duration=duration, unit_cost=unit_cost, image_url=image_url, description=description).save()
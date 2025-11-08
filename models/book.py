from models.users import User
from models.package import Package
from app import db
from mongoengine.queryset.visitor import Q

class Booking(db.Document):
    
    meta = {'collection': 'booking'}
    check_in_date = db.DateTimeField(required=True)
    customer = db.ReferenceField(User)
    package = db.ReferenceField(Package)
    total_cost = db.FloatField()
    
    def calculate_total_cost(self):
        self.total_cost = self.package.duration * self.package.unit_cost
        self.save()

    @staticmethod
    def getBookingsByEmail(email):
        customer = User.getUser(email)
        if customer:
            return Booking.objects(customer=customer)
        return []

    @staticmethod
    def getAllBookings():
        return Booking.objects()           
            
    @staticmethod
    def createBooking(check_in_date, customer, package):
        booking = Booking(check_in_date=check_in_date, customer=customer, package=package).save()
        booking.calculate_total_cost()
        return booking
              
    @staticmethod
    def getUserBookingsFromDate(customer, from_date):
        return Booking.objects(Q(customer = customer) & Q(check_in_date__gte = from_date))
               

    @staticmethod
    def getBooking(check_in_date, customer, hotel_name):
        package = Package.getPackage(hotel_name)
        return Booking.objects(Q(customer = customer) & Q(check_in_date = check_in_date) & Q(package = package)).first()

    @staticmethod
    def updateBooking(old_check_in_date, new_check_in_date, customer, hotel_name):
        booking = Booking.getBooking(old_check_in_date, customer, hotel_name)
        if booking:
            booking.check_in_date = new_check_in_date
            return booking.save()
            

    @staticmethod
    def deleteBooking(check_in_date, customer, hotel_name):
        booking = Booking.getBooking(check_in_date, customer, hotel_name)
        if booking:
            booking.delete()
        return booking
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta, date
from app import db
from models.book import Booking

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/trend_chart', methods=['GET', 'POST'])
def trend_chart():
    
    if request.method == 'GET':
        
        #I want to get some data from the service
        return render_template('trend_chart.html', panel="Package Chart")    #do nothing but to show index.html
    
    elif request.method == 'POST':
        
        #Chart is indexed by first date and last date
        #And we are going to plot the period from 2021-01-17 to 2021-01-23

        #Trend is reconstructed each time from Booking to incorporate new booking since the last trend chart

        all_bookings = Booking.getAllBookings()
        print(f"There are {len(all_bookings)} of booking records")
        #TREND.objects.delete()

        # hotel_costbyDate[hotel_name] = {date: accum_cost, ...}
        hotel_costbyDate = {}

        for aBooking in list(all_bookings):
            hotel_name = aBooking.package.hotel_name
            check_in_date = aBooking.check_in_date
                      
            if hotel_name not in hotel_costbyDate:
                hotel_costbyDate[hotel_name] = {}
            if check_in_date not in hotel_costbyDate[hotel_name]:
                hotel_costbyDate[hotel_name][check_in_date] = 0
            hotel_costbyDate[hotel_name][check_in_date] += aBooking.total_cost
        
        hotel_costbyDateSortedListValues = {}
        for hotel, dateAmts in hotel_costbyDate.items():
            hotel_costbyDateSortedListValues[hotel] = sorted(list(dateAmts.items()))

        return jsonify({'chartDim': hotel_costbyDateSortedListValues, 'labels': []})    


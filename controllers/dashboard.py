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

@dashboard.route('/bookings_by_month', methods=['POST'])
def bookings_by_month():
    """
    Aggregates bookings by month-year for each hotel.
    Returns format: {hotel_name: {month-year: count, ...}, ...}
    """
    all_bookings = Booking.getAllBookings()
    print(f"Processing {len(all_bookings)} bookings for month aggregation")

    # hotel_bookingsByMonth[hotel_name] = {month-year: count, ...}
    hotel_bookingsByMonth = {}

    for aBooking in list(all_bookings):
        hotel_name = aBooking.package.hotel_name
        check_in_date = aBooking.check_in_date

        # Format as "Month YYYY" (e.g., "January 2022")
        month_year = check_in_date.strftime("%B %Y")

        if hotel_name not in hotel_bookingsByMonth:
            hotel_bookingsByMonth[hotel_name] = {}
        if month_year not in hotel_bookingsByMonth[hotel_name]:
            hotel_bookingsByMonth[hotel_name][month_year] = 0
        hotel_bookingsByMonth[hotel_name][month_year] += 1

    # Sort hotels alphabetically
    sorted_hotel_data = dict(sorted(hotel_bookingsByMonth.items()))

    return jsonify({'chartData': sorted_hotel_data})


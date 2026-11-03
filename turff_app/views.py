from rest_framework.views import APIView
from turff_app.models import *
from turff_app.serializers import *
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from datetime import *
from rest_framework import status
from decimal import Decimal

class TurfListCreateView(APIView):

    def get(self,request):

        qs=TurfDb.objects.all()

        serializer_instance=TurffSerializer(qs,many=True)

        return Response(data=serializer_instance.data)

    def post(self,request):

        form_data=request.data

        serializer_instance=TurffSerializer(data=form_data)
        if serializer_instance.is_valid():
            serializer_instance.save()
            return Response(data=serializer_instance.data)
        else:
            return Response(data=serializer_instance.errors)

class TurfGetUpdateDelete(APIView):

    def get(self,request,t_id):

        qs=get_object_or_404(TurfDb,id=t_id)
        serializer_instance=TurffSerializer(qs)
        return Response(serializer_instance.data)

    def put(self,request,t_id):

        qs=get_object_or_404(TurfDb,id=t_id)
        serializer_instance=TurffSerializer(qs,data=request.data)
        if serializer_instance.is_valid():
            serializer_instance.save()
            return Response(data=serializer_instance.data)
        else:
            return Response(data=serializer_instance.errors)

    def delete(self,request,t_id):

        qs=get_object_or_404(TurfDb,id=t_id)
        qs.delete()
        return Response(data={'message':"deleted"})

class BookingCreateView(APIView):

    def get(self,request):

        qs=BookingDb.objects.all()

        tid=request.query_params.get("turf")
        bookingdate=request.query_params.get("booking_date")
        bookingstatus=request.query_params.get("status")

        if tid:
            qs=qs.filter(turf_id=tid)#here this turf_id means id from the turf table
        if bookingdate:
            qs=qs.filter(booking_date=bookingdate)
        if bookingstatus:
            qs=qs.filter(status=bookingstatus)

        serializer_instance=BookingSerializer(qs,many=True)

        return Response(data=serializer_instance.data)

    def post(self,request):

        form_data=request.data

        serializer_instance=BookingSerializer(data=form_data)

        if serializer_instance.is_valid():
            t_id=serializer_instance.validated_data.get("turf")
            active_or_not=t_id.is_active
            game_booking_date=serializer_instance.validated_data.get("booking_date")
            game_start_time=serializer_instance.validated_data.get("start_time")
            game_end_time=serializer_instance.validated_data.get("end_time")
            turff_opening_time=t_id.opening_time
            turff_closing_time=t_id.closing_time
            today=datetime.today().date()
            current_time=datetime.now().time()

            #check whether active or not
            if active_or_not == False:
                return Response(
                    {"error":"turff is not active now"},
                    status=status.HTTP_400_BAD_REQUEST)

            # Check whether the booking date is in the past
            if game_booking_date < today:
                return Response(
                    {"error": "Please select a valid date"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check whether the selected time is in the past (only for today)
            if game_booking_date == today and game_start_time <= current_time:
                return Response(
                    {"error": "Please select a valid time"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            #check whether endtime less than start time
            if game_end_time<=game_start_time:
                return Response(
                    {"error":"please select a valid time"},
                    status=status.HTTP_400_BAD_REQUEST)

            #check booking time is out of turff time
            if game_start_time<turff_opening_time or game_end_time>turff_closing_time or game_start_time>=turff_closing_time:
                return Response(
                    {'error':"turff close time"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            #avoid double booking
            booked_slots=BookingDb.objects.filter(turf=t_id,booking_date=game_booking_date,status__in=['pending','confirmed'])

            for book in booked_slots:

                existing_start=book.start_time
                existing_end=book.end_time

                if existing_start<game_end_time and existing_end>game_start_time :
                    return Response({"error":"slot is already booked"},status=status.HTTP_400_BAD_REQUEST)
            
            #calcuate the duration and price

            price_cal_start_time=datetime.combine(game_booking_date,game_start_time)
            price_cal_end_time=datetime.combine(game_booking_date,game_end_time)

            total_duration=price_cal_end_time-price_cal_start_time
            total_hr=(total_duration.total_seconds()/3600)

            total_price=Decimal(str(total_hr))*t_id.price_per_hr

            booking = serializer_instance.save(
                    total_price=total_price,
                    status="confirmed"
                )

            return Response({"customer name":booking.customer_name,
                             "customer phone number":booking.customer_phone,
                             "turf name":booking.turf.turf_name,
                             "booked date":booking.booking_date,
                             "booking time":booking.start_time,
                             "game ending time":booking.end_time,
                             "price":booking.total_price,
                             "status":booking.status},status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer_instance.errors,status=status.HTTP_400_BAD_REQUEST)

class BookingGetCancelDelete(APIView):

    def get(self,request,b_id):

        qs=get_object_or_404(BookingDb,id=b_id)

        serializer_instance=BookingSerializer(qs)

        return Response(data=serializer_instance.data,status=status.HTTP_200_OK)

    def put(self,request,b_id):

        form_data=request.data

        qs=get_object_or_404(BookingDb,id=b_id)

        serializer_instance=BookingSerializer(qs,data=form_data)

        if serializer_instance.is_valid():
            serializer_instance.save()

            return Response(data=serializer_instance.data,status=status.HTTP_200_OK)
        else:
            return Response(data=serializer_instance.errors,status=status.HTTP_400_BAD_REQUEST)

    def patch(self,request,b_id):

        booking=get_object_or_404(BookingDb,id=b_id)

        if booking.status=="cancelled":
            return Response(data={"message":"this booking is already cancelled"})
        else:
            booking.status='cancelled'
            booking.save()
            return Response({"message":f"{booking.id} is cancelled",
                             "booking id":booking.id,
                             "booking status":booking.status},status=status.HTTP_200_OK)

class TurffAvailability(APIView):

    def get(self,request):

        turfid=request.query_params.get("turf")
        bookingdate=request.query_params.get("date")

        #check whether turfid is given or not
        if not turfid:
            return Response({"message":"turf id is required"},status=status.HTTP_400_BAD_REQUEST)

        #check whether booking date is given or not
        if not bookingdate:
            return Response({"message":"booking date is required"},status=status.HTTP_400_BAD_REQUEST)

        #check whether the booking date in correct format
        try:
            bookingdate=datetime.strptime(bookingdate,"%Y-%m-%d").date()
        except ValueError:
            return Response({"message":"date format is wrong"},status=status.HTTP_400_BAD_REQUEST)

        #chech whether the booking id is in correct format
        try:
            turfid=int(turfid)
        except ValueError:
            return Response({'message':'invalid turf id, please give integer'},status=status.HTTP_400_BAD_REQUEST)

        #check whether the booking id is in the past
        if bookingdate<datetime.today().date():
            return Response({'message':"booking date is in the past"},status=status.HTTP_400_BAD_REQUEST)

        turf_details=get_object_or_404(TurfDb,id=turfid)
        
        #check whether the turf id active
        if not turf_details.is_active:
            return Response({"message":"turff is not active"},status=status.HTTP_400_BAD_REQUEST)

        #identifiing all the slots from the starting to ending of the date
        opening_time=turf_details.opening_time
        closing_time=turf_details.closing_time

        opening_time=datetime.combine(bookingdate,opening_time)
        closing_time=datetime.combine(bookingdate,closing_time)

        all_slots=[]
        current_time=opening_time

        while current_time+timedelta(hours=1)<=closing_time:
            next_time=current_time+timedelta(hours=1)
            all_slots.append({
                "start_time":current_time.time(),
                "end_time":next_time.time()
            })
            current_time=next_time

        c_date=datetime.today().date()
        c_time=datetime.now().time()

        if bookingdate==c_date:
            all_slots=[slot for slot in all_slots if slot['start_time']>c_time]

        #identifing which slot is available which one is not available

        already_booked_slots=BookingDb.objects.filter(turf_id=turfid,
                                                    booking_date=bookingdate,
                                                    status='confirmed')

        available_slots=[]
        for slot in all_slots:

            slot_start=slot["start_time"]
            slot_end=slot["end_time"]

            is_booked=False

            for booked in already_booked_slots:

                if slot_start<booked.end_time and slot_end>booked.start_time:

                    is_booked=True
                    break

            if not is_booked:
                available_slots.append(slot)

        return Response({
            "turf name":turf_details.turf_name,
            "date":bookingdate,
            "avaliable slots":available_slots
        })
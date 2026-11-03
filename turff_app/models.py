from django.db import models

class TurfDb(models.Model):

    turf_name=models.CharField(max_length=100)
    location=models.CharField(max_length=250)
    description=models.TextField(blank=True,null=True)

    SPORTS_TYPE=[
        ("foot_ball","Football"),
        ("cricket","Cricket")
    ]

    sports=models.CharField(max_length=10,choices=SPORTS_TYPE,default='foot_ball')
    price_per_hr=models.DecimalField(max_digits=10,decimal_places=2)
    capacity=models.PositiveIntegerField()
    opening_time=models.TimeField()
    closing_time=models.TimeField()
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.turf_name

class BookingDb(models.Model):

    customer_name=models.CharField(max_length=100)
    customer_phone=models.CharField(max_length=15)
    turf=models.ForeignKey(TurfDb,on_delete=models.CASCADE)
    booking_date=models.DateField()
    start_time=models.TimeField()
    end_time=models.TimeField()
    total_price=models.DecimalField(max_digits=10,decimal_places=2)

    STATUS_TYPE=[('cancelled','cancelled'),('confirmed','confirmed')]

    status=models.CharField(max_length=50,choices=STATUS_TYPE,default='confirmed')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.customer_name
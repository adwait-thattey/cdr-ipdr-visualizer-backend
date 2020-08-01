import math

from dateutil.parser import parse as dtparse
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from data.models import CDR
from .serializers import FullCDRSerializer, MinimalCDRSerializer, FullIPDRSerializer, MinimalIPDRSerializer


def get_filtered_queryset(query_params) -> list:
    cdr_list = CDR.objects.filter()

    # time_filter

    stime = query_params.get('time_start')
    if stime is not None:
        stime = dtparse(stime)
        cdr_list = cdr_list.filter(timestamp__gte=stime)

    etime = query_params.get('time_end')
    if etime is not None:
        etime = dtparse(etime)
        cdr_list = cdr_list.filter(timestamp__lte=etime)

    # location based filter
    location_lat = query_params.get('location_lat')
    location_long = query_params.get('location_long')
    location_radius = query_params.get('location_radius')

    if None not in [location_lat, location_long, location_radius]:
        r_earth = 6371000
        max_latitude = location_lat + (location_radius / r_earth) * (180 / 3.14);
        max_longitude = location_long + (location_radius / r_earth) * (180 / 3.14) / math.cos(location_lat * 3.14 / 180)
        min_latitude = location_lat - (location_radius / r_earth) * (180 / 3.14);
        min_longitude = location_long - (location_radius / r_earth) * (180 / 3.14) / math.cos(
            location_lat * 3.14 / 180)

        cdr_list = cdr_list.filter(location_lat__gte=min_latitude, location_lat__lte=max_latitude)
        cdr_list = cdr_list.filter(location_long__gte=min_longitude, location_long__lte=max_longitude)

    phone_numbers = query_params.getlist('phone_number')

    if phone_numbers:
        cdr_list = cdr_list.filter(phone_numbers__in=phone_numbers)

    return cdr_list


class MinimalCDRView(APIView):

    def get(self, request):
        cdr_list = get_filtered_queryset(request.query_params)
        ser = MinimalCDRSerializer(cdr_list, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)


class FullCDRView(APIView):

    def get(self, request):
        cdr_ids = request.query_params.getlist('cdr')
        relevantCDRs = get_filtered_queryset(request.query_params)
        ser = FullCDRSerializer(relevantCDRs, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)

import math

from dateutil.parser import parse as dtparse
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from data.models import CDR, MobileNumber
from .serializers import FullCDRSerializer, MinimalCDRSerializer, FullIPDRSerializer, MinimalIPDRSerializer


def get_generic_filtered_queryset(qset, query_params) -> list:
    # time_filter

    stime = query_params.get('time_start')
    if stime is not None:
        stime = dtparse(stime)
        qset = qset.filter(timestamp__gte=stime)

    etime = query_params.get('time_end')
    if etime is not None:
        etime = dtparse(etime)
        qset = qset.filter(timestamp__lte=etime)

    # duration filter
    duration_min = query_params.get('duration_min')
    duration_max = query_params.get('duration_max')

    if duration_min:
        duration_min = int(duration_min)
        qset = qset.filter(duration__gte=duration_min)
    if duration_max:
        duration_max = int(duration_max)
        qset = qset.filter(duration__lte=duration_max)

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

        qset = qset.filter(location_lat__gte=min_latitude, location_lat__lte=max_latitude)
        qset = qset.filter(location_long__gte=min_longitude, location_long__lte=max_longitude)

    phone_numbers = query_params.getlist('phone_number')

    if phone_numbers:
        qset = qset.filter(phone_numbers__in=phone_numbers)

    return qset


def get_cdr_filtered_queryset(query_params):
    qset = CDR.objects.filter()
    qset = get_generic_filtered_queryset(qset, query_params)
    return qset


class MinimalCombinedView(APIView):

    def get(self, request):
        types = request.query_params.get('type')

        cdr_data = []
        if types is None or types == "cdr" or types == "all":
            cdr_qset = get_cdr_filtered_queryset(request.query_params)
            cdr_temp_data = {}
            from_phone_numbers = set(cdr_qset.values_list('from_number', flat=True))
            to_phone_numbers = set(cdr_qset.values_list('to_number', flat=True))
            phone_numbers = from_phone_numbers.union(to_phone_numbers)
            ph_us_set = set(
                MobileNumber.objects.filter(number__in=phone_numbers).values_list('number', 'associated_person'))
            ph_us_dict = {tup[0]: tup[1] for tup in ph_us_set}

            for i in cdr_qset:
                fn = i.from_number
                tn = i.to_number
                key_string = f'{fn}-{tn}'
                if key_string not in cdr_temp_data:
                    cdr_temp_data[key_string] = list()

                cdr_temp_data[key_string].append(i.id)

            for key_str in cdr_temp_data:
                fnum, tnum = key_str.split('-')
                data_obj = {}
                data_obj['from'] = ph_us_dict[fnum]
                data_obj['to'] = ph_us_dict[tnum]
                data_obj['calls'] = cdr_temp_data[key_str]

                cdr_data.append(data_obj)

            # ser = FullCDRSerializer(cdr_qset, many=True)

            return Response({'cdrData': cdr_data}, status=status.HTTP_200_OK)


class FullCDRView(APIView):

    def get(self, request):
        # for cdr

        cdr_ids = request.query_params.getlist('cdr')
        relevantCDRs = CDR.objects.filter(id__in=cdr_ids)
        ser = FullCDRSerializer(relevantCDRs, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)

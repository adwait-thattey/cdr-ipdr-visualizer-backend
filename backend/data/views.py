import math
import random

from dateutil.parser import parse as dtparse
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from data.models import CDR, MobileNumber, Person, WatchList, IPDR, Service, Alert, AlertInstance, AlertNotification
from .serializers import FullCDRSerializer, MinimalCDRSerializer, FullIPDRSerializer, MinimalIPDRSerializer, \
    PersonFullSerializer, WatchListSerializer, ServiceSerializer, AlertSerializer, AlertInstanceSerializer

SERVICE_MAPPING = {

}

TOWER_ANALYSIS_DATA = {}


def get_generic_filtered_queryset(qset, query_params) -> list:
    # time_filter

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

    # Phone Numbers filter
    phone_numbers = query_params.getlist('phone_number')
    not_phone_numbers = query_params.getlist('not_phone_number')

    if phone_numbers:
        qset = qset.filter(from_number__in=phone_numbers)

    qset = qset.exclude(from_number__in=not_phone_numbers)

    # IMEI filter
    imei_numbers = query_params.getlist('imei')
    not_imei_numbers = query_params.getlist('not_imei')

    if imei_numbers:
        qset = qset.filter(imei__in=imei_numbers)

    qset = qset.exclude(imei__in=not_imei_numbers)

    # IMEI filter
    imsi_numbers = query_params.getlist('imsi')
    not_imsi_numbers = query_params.getlist('not_imsi')

    if imsi_numbers:
        qset = qset.filter(imei__in=imsi_numbers)

    qset = qset.exclude(imsi__in=not_imsi_numbers)

    return qset


def get_cdr_filtered_queryset(query_params, cdr_qset=None):
    if cdr_qset is None:
        qset = CDR.objects.filter()
    else:
        qset = cdr_qset

    qset = get_generic_filtered_queryset(qset, query_params)

    stime = query_params.get('time_start')
    if stime is not None:
        stime = dtparse(stime)
        qset = qset.filter(timestamp__gte=stime)

    etime = query_params.get('time_end')
    if etime is not None:
        etime = dtparse(etime)
        qset = qset.filter(timestamp__lte=etime)

    return qset


def get_ipdr_filtered_queryset(query_params, ipdr_qset=None):
    if ipdr_qset is None:
        qset = IPDR.objects.filter()
    else:
        qset = ipdr_qset

    qset = get_generic_filtered_queryset(qset, query_params)

    stime = query_params.get('time_start')
    if stime is not None:
        stime = dtparse(stime)
        qset = qset.filter(start_time__gte=stime)

    etime = query_params.get('time_end')
    if etime is not None:
        etime = dtparse(etime)
        qset = qset.filter(start_time__lte=etime)
    return qset


class MinimalCombinedView(APIView):

    def get(self, request):
        types = request.query_params.get('type')

        cdr_data = []
        ipdr_data = []
        only_user_ids = set([int(i) for i in request.query_params.getlist('user_id')])
        not_user_ids = set([int(i) for i in request.query_params.getlist('not_user_id')])

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

                if only_user_ids:

                    if data_obj['from'] not in only_user_ids or data_obj['to'] not in only_user_ids:
                        continue
                if data_obj['from'] in not_user_ids or data_obj['to'] in not_user_ids:
                    continue
                cdr_data.append(data_obj)

            # ser = FullCDRSerializer(cdr_qset, many=True)

        if types is None or types == "ipdr" or types == "all":
            ipdr_qset = get_ipdr_filtered_queryset(request.query_params)
            ipdr_temp_data = {}
            from_phone_numbers = set(ipdr_qset.values_list('from_number', flat=True))
            phone_numbers = from_phone_numbers
            ph_us_set = set(
                MobileNumber.objects.filter(number__in=phone_numbers).values_list('number', 'associated_person'))
            ph_us_dict = {tup[0]: tup[1] for tup in ph_us_set}

            ip_serv_set = set(Service.objects.all().values_list('ip', 'id'))
            ip_serv_dict = {tup[0]: tup[1] for tup in ip_serv_set}

            for i in ipdr_qset:
                fn = i.from_number
                tn = i.destination_ip
                key_string = f'{fn}-{tn}'
                if key_string not in ipdr_temp_data:
                    ipdr_temp_data[key_string] = list()

                ipdr_temp_data[key_string].append(i.id)

            for key_str in ipdr_temp_data:
                fnum, tnum = key_str.split('-')
                data_obj = {}
                data_obj['from'] = ph_us_dict[fnum]
                if tnum in ip_serv_dict:
                    data_obj['to'] = ip_serv_dict[tnum]
                else:
                    data_obj['to'] = -1

                data_obj['calls'] = ipdr_temp_data[key_str]

                if only_user_ids:

                    if data_obj['from'] not in only_user_ids:
                        continue
                if data_obj['from'] in not_user_ids:
                    continue
                ipdr_data.append(data_obj)

        return Response({'cdrData': cdr_data, 'ipdrData': ipdr_data}, status=status.HTTP_200_OK)


class FullCDRView(APIView):

    def get(self, request):
        # for cdr

        cdr_ids = request.query_params.getlist('cdr')
        relevantCDRs = CDR.objects.filter(id__in=cdr_ids)
        ser = FullCDRSerializer(relevantCDRs, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)


class FullIPDRView(APIView):

    def get(self, request):
        # for cdr
        ipdr_ids = request.query_params.getlist('ipdr')
        relevantIPDRs = IPDR.objects.filter(id__in=ipdr_ids)
        ser = FullIPDRSerializer(relevantIPDRs, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)


class DetailedPersonView(APIView):

    def get(self, request):
        person_ids = request.query_params.getlist('person')
        relevant_persons = Person.objects.filter(id__in=person_ids)
        ser = PersonFullSerializer(relevant_persons, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)


class UserTimelineView(APIView):

    def get(self, request, user_id):
        numbers = set(MobileNumber.objects.filter(associated_person__id=int(user_id)).values_list('number', flat=True))
        cdr_data = CDR.objects.filter(from_number__in=numbers)

        cdr_data = get_cdr_filtered_queryset(request.query_params, cdr_data)

        ser = FullCDRSerializer(cdr_data, many=True)

        cdr_data = ser.data
        for o in cdr_data:
            o["type"] = "cdr"

        ipdr_data = IPDR.objects.filter(from_number__in=numbers)

        ipdr_data = get_ipdr_filtered_queryset(request.query_params, ipdr_data)

        ipser = FullIPDRSerializer(ipdr_data, many=True)

        ipdr_data = ipser.data
        for o in ipdr_data:
            o["type"] = "ipdr"

        cdr_data.extend(ipdr_data)

        return Response(cdr_data, status=status.HTTP_200_OK)


class WatchListView(APIView):

    def get(self, request):
        w = WatchList.objects.all()
        ser = WatchListSerializer(w, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)

    def post(self, request):
        wid = request.data.get('id')
        ws = None
        if wid:
            obj = WatchList.objects.filter(id=wid)
            if obj:
                ws = WatchListSerializer(obj, data=request.data)

        if not ws:
            ws = WatchListSerializer(data=request.data)

        if ws.is_valid():
            w = ws.save()
            return Response(ws.data, status=status.HTTP_201_CREATED)
        else:
            return Response(ws.errors, status=status.HTTP_400_BAD_REQUEST)


class ServiceView(APIView):

    def get(self, request):
        ids = request.query_params.getlist('service')
        services = Service.objects.filter(id__in=ids)
        ser = ServiceSerializer(services, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)


class AlertView(APIView):

    def get(self, request):
        alerts = Alert.objects.all()
        ser = AlertSerializer(alerts, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)

    def post(self, request):
        ser = AlertSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        else:
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        alertId = request.data.get('id')
        if alertId:
            alert = Alert.objects.filter(id=int(alertId))
            if alert.exists():
                alert.delete()
                return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class AlertInstanceView(APIView):

    def get(self, request):
        alertinstances = AlertInstance.objects.all().order_by('-timestamp')
        ser = AlertInstanceSerializer(alertinstances, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)


class AlertNotificationView(APIView):

    def get(self, request):
        notifs = AlertInstance.objects.filter(alertnotification__is_seen=False)
        ser = AlertInstanceSerializer(notifs, many=True)
        for n in notifs:
            n.alertnotification.is_seen = True
            n.alertnotification.save()
        return Response(ser.data, status=status.HTTP_200_OK)


class TowerAnalysis(APIView):
    def get(self, request, towerid):

        if towerid in TOWER_ANALYSIS_DATA:
            return Response(TOWER_ANALYSIS_DATA[towerid], status=status.HTTP_200_OK)

        cdr_data = CDR.objects.filter(cell_id=towerid)
        ipdr_data = IPDR.objects.filter(cell_id=towerid)

        stats = {}

        stats['Total CDR Logs'] = cdr_data.count()
        stats['Total IPDR Logs'] = ipdr_data.count()

        if cdr_data.count() > 0:
            stats['Average Daily Traffic'] = random.randint(10, 100)
        else:
            stats['Average Daily Traffic'] = 0

        service_share = {}
        if ipdr_data.count() > 0:

            unique_ips = ipdr_data.values_list('destination_ip', flat=True).distinct()

            for ip in unique_ips:
                val = random.randint(100, 2000)
                if ip in SERVICE_MAPPING:
                    service_share[SERVICE_MAPPING[ip]] = val
                else:
                    service_share[f'Unknown Service {ip}'] = val

        combined_res = {'stats': stats, 'service_share': service_share}
        TOWER_ANALYSIS_DATA[towerid] = combined_res

        return Response(combined_res, status=status.HTTP_200_OK)

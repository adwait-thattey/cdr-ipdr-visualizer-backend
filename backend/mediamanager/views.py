from django.shortcuts import render
from rest_framework import status
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response

from .serializers import MediaManagerSerializer
# Create your views here.
from rest_framework.views import APIView
from .speech_recog_views import speech2text

from detect_person.person_recog_views import get_name
class MediaManagerView(APIView):
    parser_class = (FileUploadParser,)

    def post(self, request, *args, **kwargs):
        ser = MediaManagerSerializer(data=request.data)
        if ser.is_valid():
            obj = ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        else:
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class CDRUploadView(APIView):
    parser_class = (FileUploadParser,)

    def post(self, request, *args, **kwargs):
        ser = MediaManagerSerializer(data=request.data)
        if ser.is_valid():
            obj = ser.save()

            return Response(ser.data, status=status.HTTP_201_CREATED)
        else:
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class SpeechUploadView(APIView):
    parser_class = (FileUploadParser,)

    def post(self, request, *args, **kwargs):
        ser = MediaManagerSerializer(data=request.data)
        if ser.is_valid():
            obj = ser.save()
            context = speech2text(obj.media_file.path)
            return Response(context, status=status.HTTP_201_CREATED)
        else:
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class PersonDetectionUploadView(APIView):
    parser_class = (FileUploadParser,)

    def post(self, request, *args, **kwargs):
        ser = MediaManagerSerializer(data=request.data)
        if ser.is_valid():
            obj = ser.save()
            context = get_name(obj.media_file.path)
            return Response(context, status=status.HTTP_201_CREATED)
        else:
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class IPDRUploadView(APIView):
    parser_class = (FileUploadParser,)

    def post(self, request, *args, **kwargs):
        ser = MediaManagerSerializer(data=request.data)
        if ser.is_valid():
            obj = ser.save()

            return Response(ser.data, status=status.HTTP_201_CREATED)
        else:
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

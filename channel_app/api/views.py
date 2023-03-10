from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from channel_app.api.serializers import ImageUploadSerializer
from channel_app.models import Image


class ImageUpload(CreateAPIView):
    serializer_class = ImageUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            image = serializer.validated_data.get('image')
            Image.objects.create(image=image)
            return Response({'status': status.HTTP_200_OK,
                             'message': 'Image Uploaded Successfully'})
        return Response({'status': status.HTTP_400_BAD_REQUEST,
                         'message': 'validation Error'})

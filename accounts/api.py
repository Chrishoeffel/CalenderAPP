import uuid

import shortuuid
from dj_rest_auth.registration.views import RegisterView
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import filters
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import ReadOnlyModelViewSet
from datetime import datetime, timedelta
from calendar import HTMLCalendar, week
from .models import Event

from .models import Avatar, Calendar_Event
from .permissions import IsSelf
from .serializers import (
    AvatarSerializer,
    UserSerializer,
    UserDetailSerializer,
    UserSearchSerializer,
)

User = get_user_model()

class UserViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet,
):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsSelf]

    def get_serializer_class(self):
        if self.action == "retrieve" or self.action == "update":
            return UserDetailSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=["post"])
    def update_avatar(self, request, pk):
        avatar_id = request.data.get("id")
        avatar = Avatar.objects.get(id=avatar_id)
        user = self.get_object()
        user.avatar = avatar
        user.save()
        return Response(AvatarSerializer(instance=avatar).data)


class AvatarViewSet(ReadOnlyModelViewSet):
    serializer_class = AvatarSerializer
    queryset = Avatar.objects.all()
    permission_classes = [IsAuthenticated]

class AuthSetup(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"ALLOW_GUEST_ACCESS": settings.ALLOW_GUEST_ACCESS})

class GuestRegistration(RegisterView):
    def create(self, request, *args, **kwargs):
        if not settings.ALLOW_GUEST_ACCESS:
            raise PermissionDenied

        password = str(uuid.uuid4())
        guest_id = str(shortuuid.uuid())[:10]
        request.data.update(
            {
                "username": f"Guest-{guest_id}",
                "email": f"{guest_id}@guest.com",
                "password1": password,
                "password2": password,
            }
        )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = super().perform_create(serializer)
        user.is_guest = True
        user.avatar = get_random_avatar()
        user.save()
        return user
    
class Calendar(HTMLCalendar):
    def __init__(self, year=none, month=None):
        self.year = year
        self.month = month
        super(Calendar, self).__init__()
    def formatday(self, day, events):
        events_per_day = events.filter(Start_time_day=day)
        d = ""
        for event in events_per_day:
            d += f'<li> {event.title}</li>'
        if day !=0:
            return f"<td><span class='date'>{day}<ul> {d}</ul></td>"
        return '<td></td>'
    def formatweek(self,theweek, events):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, events)
        return f'<td> {week} </td>'
    
    
    def formatmonth(self, withyear=True):
        events = Calendar_Event.objects.filter(start_time_year=self.year, start_time_month=self.month)
        
        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
		cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
			cal += f'{self.formatweek(week, events)}\n'
		return cal
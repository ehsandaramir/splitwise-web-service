from django.http import Http404
from rest_framework import mixins, viewsets, permissions, status, generics
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response

from split_wise import serializers
from split_wise.models import *


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
def api_signup(request):
    serializer = serializers.UserSerializer(data=request.data, context={'request': request})
    serializer.is_valid(True)
    serializer.save()
    return Response(serializer.data)


class ProfileViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """
    retrieve profile model objects
    """
    queryset = Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    authentication_classes = (TokenAuthentication,)


class UserViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    # mixins.UpdateModelMixin,
    # mixins.DestroyModelMixin
):
    """
    view set for CRUD django default user model
    note1: there is a Profile model that is one-to-one with user model
    """
    serializer_class = serializers.UserSerializer
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticatedOrCreateOnly,)

    def get_queryset(self):
        if self.request.query_params:
            result = []
            result += User.objects.filter(username__contains=self.request.query_params.get('q', ''))
            result += User.objects.filter(email__contains=self.request.query_params.get('q', ''))

            username_set = set()
            final_result = list()
            for i in result:
                if i.username not in username_set:
                    username_set.add(i.username)
                    final_result.append(i)

            final_result = sorted(final_result, key=lambda instance: instance.date_joined)
            return final_result
        else:
            return User.objects.all()

    def get_object(self):
        if self.request.method in permissions.SAFE_METHODS:
            return User.objects.get(pk=self.kwargs.get('pk'))
        else:
            if int(self.kwargs.get('pk')) == self.request.user.id:
                return self.request.user
            else:
                raise PermissionDenied('could not change user that is not you!')


class SelfUserDetail(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        instance = self.request.user
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        # partial = kwargs.pop('partial', False)
        partial = True
        instance = request.user
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BillViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """
    CRUD objects of Bill entity
    note: balanced is not required when creating object
    """
    serializer_class = serializers.BillSerializer
    permission_classes = (IsAuthenticated, )
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        current_user = self.request.user
        groups = current_user.bill_groups.all()

        result = []
        for group in groups:
            for bill in group.bills.all():
                result.append(bill)
        return result

    def get_object(self):
        for val in self.get_queryset():
            if val.id == int(self.kwargs.get('pk')):
                return val
        raise Http404()

    def create(self, request, *args, **kwargs):
        request.data['creator__write'] = request.user.id
        return super().create(request, *args, **kwargs)


class BillInstantViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = serializers.BillInstantSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        current_user = self.request.user
        groups = current_user.bill_groups.all()

        result = []
        for group in groups:
            for bill in group.bills.all():
                result.append(bill)
        return result

    def get_object(self):
        for val in self.get_queryset():
            if val.id == int(self.kwargs.get('pk')):
                return val
        raise Http404()

    def create(self, request, *args, **kwargs):
        request.data['creator__write'] = request.user.id
        return super().create(request, *args, **kwargs)


class TransactionViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin
):
    serializer_class = serializers.TransactionSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        current_user = self.request.user
        groups = current_user.bill_groups.all()

        result = []
        for group in groups:
            for bill in group.bills.all():
                for trans in bill.transactions.all():
                    result.append(trans)
        return result

    def get_object(self):
        for val in self.get_queryset():
            if val.id == int(self.kwargs.get('pk')):
                return val
        raise Http404()


class GroupViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

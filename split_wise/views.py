from itertools import chain

from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import mixins, viewsets, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response

from split_wise import serializers
from split_wise.models import Profile, Bill, Payment, Debt


class ProfileViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """
    retrieve profile model objects

    list:
        list of all created profiles
        note: paginated!

    retrieve:
        get an specified profile
        note: represented by url

    """
    queryset = Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    authentication_classes = (SessionAuthentication, BasicAuthentication)


class UserViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin
):
    """
    view set for list / detail / update / delete  django default user model
    note1: there is a Profile model that is one-to-one with user model
    note2: for create user post on '/api/self/user/' url
    """
    serializer_class = serializers.UserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    authentication_classes = (SessionAuthentication, BasicAuthentication)

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


class BillViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = serializers.BillSerializer
    permission_classes = (IsAuthenticated, )
    authentication_classes = (SessionAuthentication, BasicAuthentication)

    def get_queryset(self):
        current_user = self.request.user
        query_set_create = Bill.objects.filter(creator=current_user)
        query_set_paid_by = Bill.objects.filter(payments__paid_by=current_user)
        query_set_owed_by = Bill.objects.filter(debts__owed_by=current_user)

        query_set = list(chain(query_set_create, query_set_paid_by, query_set_owed_by))

        username_set = set()
        final_result = list()
        for i in query_set:
            if i.id not in username_set:
                username_set.add(i.id)
                final_result.append(i)

        final_result = sorted(final_result, key=lambda instance: instance.create_date)
        return final_result

    def create(self, request, *args, **kwargs):
        request.data['creator'] = request.user.id
        return super().create(request, *args, **kwargs)


class PaymentViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = serializers.PaymentSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication, BasicAuthentication)

    def get_queryset(self):
        current_user = self.request.user
        you_paid = Payment.objects.filter(paid_by=current_user)
        paid_to_you = Payment.objects.filter(bill__debts__owed_by=current_user)

        result = chain(you_paid, paid_to_you)
        result = sorted(result, key=lambda instance: instance.bill.create_date)
        return result


class DebtViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = serializers.DebtSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication, BasicAuthentication)

    def get_queryset(self):
        current_user = self.request.user
        you_paid = Debt.objects.filter(owed_by=current_user)
        paid_to_you = Debt.objects.filter(bill__payments__paid_by=current_user)

        result = chain(you_paid, paid_to_you)
        result = sorted(result, key=lambda instance: instance.bill.create_date)
        return result


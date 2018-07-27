from itertools import chain

from django.contrib.auth.models import User
from django.http import Http404
from rest_framework import mixins, viewsets, permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from split_wise import serializers
from split_wise.models import Profile, Bill, Payment, Debt


class ProfileViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """
    retrieve profile model objects
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
    view set for CRUD django default user model
    note1: there is a Profile model that is one-to-one with user model
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

    def get_object(self):
        if self.request.method in permissions.SAFE_METHODS:
            return User.objects.get(pk=self.kwargs.get('pk'))
        else:
            if int(self.kwargs.get('pk')) == self.request.user.id:
                return self.request.user
            else:
                raise PermissionDenied('could not change user that is not you!')


class BalanceViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin
):
    serializer_class = serializers.BillSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication, BasicAuthentication)

    def base_queryset(self):
        current_user = self.request.user
        query_set_create = Bill.objects.filter(creator=current_user)
        query_set_paid_by = Bill.objects.filter(payments__paid_by=current_user)
        query_set_owed_by = Bill.objects.filter(debts__owed_by=current_user)

        query_set = list(chain(query_set_create, query_set_paid_by, query_set_owed_by))

        # username_set = set()
        # final_result = list()
        # for i in query_set:
        #     if i.id not in username_set:
        #         username_set.add(i.id)
        #         final_result.append(i)

        final_result = sorted(query_set, key=lambda instance: instance.create_date)
        return final_result

    def get_queryset(self):
        return [b for b in self.base_queryset() if b.balance >= 0.01 or b.balance <= -0.01]

    def get_object(self):
        for b in self.get_queryset():
            if b.id == int(self.kwargs.get('pk')):
                return b
        raise Http404()


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

    def get_object(self):
        for val in self.get_queryset():
            if val.id == int(self.kwargs.get('pk')):
                return val
        raise Http404()

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
    """
    CRUD for payment entity,
    payment indicates money that spent under this bill and by who
    """
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

    def get_object(self):
        for val in self.get_queryset():
            if val.id == int(self.kwargs.get('pk')):
                return val
        raise Http404()


class DebtViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """
    CRUD for Debt entity,
    debt indicates the money that must be returned to payers
    """
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

    def get_object(self):
        for val in self.get_queryset():
            if val.id == int(self.kwargs.get('pk')):
                return val
        raise Http404()

from django.contrib.auth.models import User
from rest_framework import serializers

from split_wise.models import Profile, Bill, Payment, Debt


class ProfileSerializer(serializers.ModelSerializer):
    # user = serializers.StringRelatedField(many=False)

    class Meta:
        model = Profile
        fields = ['user', 'first_name', 'last_name', ]
        read_only_fields = ['user', ]
        depth = 1


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['pk', 'username', 'email', 'password', 'profile', ]
        read_only_fields = ['pk', ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', None)
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        profile_ser = ProfileSerializer(user.profile, data=profile_data)
        if profile_ser.is_valid():
            profile_ser.save()
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data['username']
        instance.email = validated_data['email']
        instance.set_password(validated_data['password'])
        instance.save()

        profile_ser = ProfileSerializer(instance.profile, data=validated_data['profile'])
        if profile_ser.is_valid(True):
            profile_ser.update(instance.profile, validated_data['profile'])

        return instance


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = ['pk', 'bill', 'paid_by', 'amount']
        read_only_fields = ['pk', ]


class DebtSerializer(serializers.ModelSerializer):

    class Meta:
        model = Debt
        fields = ['pk', 'bill', 'owed_by', 'amount']
        read_only_fields = ['pk', ]


class BillSerializer(serializers.ModelSerializer):
    creator = UserSerializer()
    payments = PaymentSerializer(many=True)
    debts = DebtSerializer(many=True)

    class Meta:
        model = Bill
        fields = ['pk', 'creator', 'title', 'desc', 'create_date', 'amount', 'payments', 'debts', ]
        read_only_fields = ['pk', 'create_date', 'payments', 'debts']
        depth = 1


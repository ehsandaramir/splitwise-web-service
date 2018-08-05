from django.contrib.auth.models import User
from rest_framework import serializers

from split_wise.models import Profile, Bill, Payment, Debt


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(read_only=True, view_name='user-detail')

    class Meta:
        model = Profile
        fields = ['url', 'user', 'first_name', 'last_name', ]
        read_only_fields = ['user', ]
        depth = 1


class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['url', 'pk', 'username', 'email', 'password', 'profile', 'bills', ]
        read_only_fields = ['pk', 'bills', ]
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
        if 'username' in validated_data:
            instance.username = validated_data['username']
        if 'email' in validated_data:
            instance.email = validated_data['email']
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()

        if 'profile' in validated_data:
            profile_ser = ProfileSerializer(instance.profile, data=validated_data['profile'])
            if profile_ser.is_valid(True):
                profile_ser.update(instance.profile, validated_data['profile'])

        return instance


class PaymentSerializer(serializers.HyperlinkedModelSerializer):
    paid_by__read = UserSerializer(source='paid_by', read_only=True)
    paid_by__write = serializers.PrimaryKeyRelatedField(source='paid_by', queryset=User.objects.all(), write_only=True)

    bill__read = serializers.HyperlinkedRelatedField(source='bill', view_name='bill-detail', read_only=True)
    bill__write = serializers.PrimaryKeyRelatedField(source='bill', queryset=Bill.objects.all(), write_only=True)

    class Meta:
        model = Payment
        fields = ['url', 'pk', 'bill__read', 'bill__write', 'paid_by__read', 'paid_by__write', 'amount']
        read_only_fields = ['pk', ]


class DebtSerializer(serializers.HyperlinkedModelSerializer):
    owed_by = UserSerializer()

    class Meta:
        model = Debt
        fields = ['url', 'pk', 'bill', 'owed_by', 'amount']
        read_only_fields = ['pk', ]


class BillSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserSerializer(many=False, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    debts = DebtSerializer(many=True, read_only=True)

    class Meta:
        model = Bill
        fields = ['url', 'pk', 'creator', 'title', 'desc', 'create_date', 'amount', 'balance', 'payments', 'debts', ]
        read_only_fields = ['url', 'pk', 'creator', 'create_date', 'payments', 'debts', 'balance']
        # depth = 1

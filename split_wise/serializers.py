from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from split_wise.models import *


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(read_only=True, view_name='user-detail')

    class Meta:
        model = Profile
        fields = ['url', 'user', 'avatar']
        read_only_fields = ('url', 'avatar')
        depth = 1


class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ('url', 'pk', 'username', 'first_name', 'last_name', 'email', 'password', 'profile', 'bill_groups')
        read_only_fields = ('url', 'pk', 'bills', 'bill_groups')
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
        if 'first_name' in validated_data:
            instance.username = validated_data['first_name']
        if 'last_name' in validated_data:
            instance.username = validated_data['last_name']
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


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    # user = UserSerializer(read_only=True)
    user = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True)
    user__write = serializers.PrimaryKeyRelatedField(source='user', queryset=User.objects.all(), write_only=True)

    bill = serializers.HyperlinkedRelatedField(view_name='bill-detail', read_only=True)
    bill__write = serializers.PrimaryKeyRelatedField(source='bill', queryset=Bill.objects.all(), write_only=True)

    class Meta:
        model = Transaction
        fields = ('url', 'pk', 'bill', 'bill__write', 'user', 'user__write', 'amount', 'direction')
        read_only_fields = ('pk',)


class BillSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserSerializer(many=False, read_only=True)
    # creator = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True)
    creator__write = serializers.PrimaryKeyRelatedField(source='creator', queryset=User.objects.all(), write_only=True)

    group = serializers.HyperlinkedRelatedField(view_name='group-detail', read_only=True)
    group__write = serializers.PrimaryKeyRelatedField(source='group', queryset=Group.objects.all(), write_only=True)

    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Bill
        fields = ('url', 'pk',
                  'creator', 'creator__write', 'group', 'group__write',
                  'transactions', 'title', 'create_date', 'amount')
        read_only_fields = ('url', 'pk', 'create_date')
        # depth = 1


class BillInstantSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserSerializer(many=False, read_only=True)
    # creator = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True)
    creator__write = serializers.PrimaryKeyRelatedField(source='creator', queryset=User.objects.all(), write_only=True)

    group = serializers.HyperlinkedRelatedField(view_name='group-detail', read_only=True)
    group__write = serializers.PrimaryKeyRelatedField(source='group', queryset=Group.objects.all(), write_only=True)

    transactions = TransactionSerializer(many=True)

    # transactions__write = TransactionSerializer(many=True, write_only=True)

    class Meta:
        model = Bill
        fields = ('url', 'pk',
                  'creator', 'creator__write', 'group', 'group__write',
                  'transactions', 'title', 'create_date', 'amount')
        read_only_fields = ('url', 'pk', 'create_date')

    def create(self, validated_data):
        transaction_data = validated_data.pop('transactions', None)
        bill = Bill.objects.create(**validated_data)
        bill.save()

        for item in transaction_data:
            item['bill__write'] = bill.id
            item['user__write'] = item['user'].id
            trans_serializer = TransactionSerializer(data=item, many=False)
            if trans_serializer.is_valid():
                trans_serializer.save()
            else:
                bill.delete()
                raise (ValidationError('transaction item is not valid'))
        return bill

    def update(self, instance, validated_data):
        # TODO: Implement
        pass


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    users = UserSerializer(many=True, read_only=True)
    # users = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True)
    users__write = serializers.PrimaryKeyRelatedField(source='users', queryset=User.objects.all(), write_only=True,
                                                      many=True)

    class Meta:
        model = Group
        fields = ('title', 'date_created', 'users', 'users__write')
        read_only_fields = ('date_created',)
        depth = 1

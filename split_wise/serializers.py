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
            instance.first_name = validated_data['first_name']
        if 'last_name' in validated_data:
            instance.last_name = validated_data['last_name']
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
    # user = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True)
    user__read = serializers.PrimaryKeyRelatedField(source='user', read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)

    bill__read = serializers.HyperlinkedRelatedField(source='bill', view_name='bill-detail', read_only=True)
    bill = serializers.PrimaryKeyRelatedField(queryset=Bill.objects.all(), write_only=True)

    class Meta:
        model = Transaction
        fields = ('url', 'pk', 'bill', 'bill__read', 'user', 'user__read', 'amount', 'direction')
        read_only_fields = ('pk',)


class BillSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserSerializer(many=False, read_only=True)
    # creator = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True)
    creator__write = serializers.PrimaryKeyRelatedField(source='creator', queryset=User.objects.all(), write_only=True)

    group = serializers.PrimaryKeyRelatedField(read_only=True)
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
    # creator__write = serializers.PrimaryKeyRelatedField(source='creator', queryset=User.objects.all(), write_only=True)

    group = serializers.HyperlinkedRelatedField(view_name='group-detail', read_only=True)
    group__write = serializers.PrimaryKeyRelatedField(source='group', queryset=Group.objects.all(), write_only=True)

    transactions = TransactionSerializer(many=True)

    class Meta:
        model = Bill
        fields = ('url', 'pk',
                  'creator', 'group', 'group__write',
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

    def update(self, instance: Bill, validated_data):
        if 'title' in validated_data:
            instance.title = validated_data['title']
        if 'amount' in validated_data:
            instance.amount = validated_data['amount']
        instance.save()

        # if 'transactions' in validated_data:
        #     current = instance.transactions.all()
        #     for trans in current:
        #         trans.delete()
        #
        #     created = []
        #
        #     for item in validated_data['transactions']:
        #         item['bill__write'] = item['bill'].id
        #         item['user__write'] = item['user'].id
        #         trans_serializer = TransactionSerializer(data=item, many=False)
        #         if trans_serializer.is_valid():
        #             trans_serializer.save()
        #             # created.append(trans_serializer.instance)
        #         else:
        #             for trans in created:
        #                 trans.delete()
        #             raise (ValidationError('transaction item is not valid'))

        return instance


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    users = UserSerializer(many=True, read_only=True)
    # users = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True)
    users__write = serializers.PrimaryKeyRelatedField(source='users', queryset=User.objects.all(), write_only=True,
                                                      many=True)
    bills = BillSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ('url', 'pk', 'title', 'date_created', 'users', 'users__write', 'bills')
        read_only_fields = ('date_created',)
        depth = 1

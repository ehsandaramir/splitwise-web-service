from rest_framework import serializers

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
    user = UserSerializer(read_only=True)
    user__write = serializers.PrimaryKeyRelatedField(source='user', queryset=User.objects.all(), write_only=True)

    bill = serializers.HyperlinkedRelatedField(view_name='bill-detail', read_only=True)
    bill__write = serializers.PrimaryKeyRelatedField(source='bill', queryset=Bill.objects.all(), write_only=True)

    class Meta:
        model = Transaction
        fields = ['url', 'pk', 'bill', 'bill__write', 'user', 'user__write', 'amount', 'direction']
        read_only_fields = ['pk', ]


class BillSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserSerializer(many=False, read_only=True)
    creator__write = serializers.PrimaryKeyRelatedField(source='creator', queryset=User.objects.all(), write_only=True)

    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Bill
        fields = ['url', 'pk', 'creator', 'creator__write', 'title', 'create_date', 'amount', 'direction']
        read_only_fields = ['url', 'pk', 'creator', 'create_date']
        # depth = 1


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    users = UserSerializer(many=True, read_only=True)
    users__write = serializers.PrimaryKeyRelatedField(source='users', queryset=User.objects.all(), write_only=True,
                                                      many=True)

    class Meta:
        model = Group
        fields = ('title', 'date_created', 'users', 'users__write')
        read_only_fields = ('date_created',)
        depth = 1

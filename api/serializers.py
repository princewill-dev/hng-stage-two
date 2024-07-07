from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['userId', 'firstName', 'lastName', 'email', 'password', 'phone']
        extra_kwargs = {
            'password': {'write_only': True},
            'userId': {'read_only': True}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).create(validated_data)

class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['userId', 'firstName', 'lastName', 'email', 'phone']
    


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ['orgId', 'name', 'description', 'created_by']
        extra_kwargs = {'created_by': {'read_only': True}}

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super(OrganisationSerializer, self).create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            "orgId": representation.get('orgId', ''),
            "name": representation.get('name', ''),
            "description": representation.get('description', '')
        }
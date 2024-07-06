from rest_framework import serializers
from .models import CustomUser, Organisation

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['userId', 'email', 'firstName', 'lastName', 'phone', 'created', 'is_active', 'is_staff', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value

    def validate_phone(self, value):
        if len(value) != 11 or not value.isdigit():
            raise serializers.ValidationError("Phone number must be 11 digits.")
        return value
    
    def validate_firstName(self, value):
        if value.strip() == "":
            raise serializers.ValidationError("First name field must not be empty.")
        return value
    
    def validate_lastName(self, value):
        if value.strip() == "":
            raise serializers.ValidationError("Last name field must not be empty.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ['orgId', 'name', 'description']

        

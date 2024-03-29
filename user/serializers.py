from rest_framework import serializers
from .models import CustomUser


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'password', 'password2', 'money']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        return CustomUser.objects.create(**validated_data)


    def save(self):
        user = CustomUser(email=self.validated_data['email'],
                          phone_number=self.validated_data['phone_number'],
                          first_name=self.validated_data['first_name'],
                          last_name=self.validated_data['last_name'],
                          )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        user.set_password(password)
        user.money = self.validated_data['money']
        user.save()
        return user


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(style={"input_type": "password"}, required=True)
    new_password = serializers.CharField(style={"input_type": "password"}, required=True)

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError({'current_password': 'Does not match'})
        return value

from rest_framework import serializers

from main.models import ShoppingList


class CreateAccountSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=255)
    confirm_password = serializers.CharField(max_length=255)

    def validate(self, attrs):
        if len(attrs.get("password")) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters")

        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError("Passwords do not match")

        return attrs


class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField(max_length=300)
    password = serializers.CharField(max_length=255)


class ShoppingListSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=169)
    quantity = serializers.IntegerField()
    note = serializers.CharField(allow_blank=True, allow_null=True, required=False)


class ShoppingListModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = ["id", "name", "quantity", "note", "created_at", "updated_at"]

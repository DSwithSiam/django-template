"""Contact serializers."""

from rest_framework import serializers

from apps.contact.models import FAQ, ContactMessage, Policy, Terms


class TermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terms
        fields = ("id", "title", "content", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = ("id", "title", "content", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ("id", "question", "answer", "order", "status", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ("id", "full_name", "email", "phone", "message", "is_replied", "created_at")
        read_only_fields = ("id", "is_replied", "created_at")
        extra_kwargs = {
            "phone": {"required": False},
        }

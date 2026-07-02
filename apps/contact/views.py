"""Contact views — thin controllers using standard response envelope."""

from rest_framework import generics, status
from rest_framework.permissions import AllowAny

from apps.contact import services as contact_services
from apps.contact.models import FAQ, ContactMessage, Policy, Terms
from apps.contact.serializers import (
    ContactMessageSerializer,
    FAQSerializer,
    PolicySerializer,
    TermsSerializer,
)
from apps.core.pagination import NoPagination
from apps.core.permissions import IsAdmin, IsAdminOrReadOnly
from apps.core.responses import success_response


# ---------------------------------------------------------------------------
# Terms & Policy (singleton-like: get_or_create pk=1)
# ---------------------------------------------------------------------------
class TermsAPIView(generics.RetrieveUpdateAPIView):
    """Retrieve or update terms and conditions."""

    serializer_class = TermsSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = NoPagination
    http_method_names = ["get", "patch"]

    def get_object(self):
        obj, _ = Terms.objects.get_or_create(pk=1)
        return obj

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return success_response("Terms retrieved.", data=serializer.data)

    def partial_update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response("Terms updated.", data=serializer.data)


class PolicyAPIView(generics.RetrieveUpdateAPIView):
    """Retrieve or update privacy policy."""

    serializer_class = PolicySerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = NoPagination
    http_method_names = ["get", "patch"]

    def get_object(self):
        obj, _ = Policy.objects.get_or_create(pk=1)
        return obj

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return success_response("Policy retrieved.", data=serializer.data)

    def partial_update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response("Policy updated.", data=serializer.data)


# ---------------------------------------------------------------------------
# FAQ
# ---------------------------------------------------------------------------
class FAQListCreateAPIView(generics.ListCreateAPIView):
    """List all FAQs or create a new one."""

    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [IsAdminOrReadOnly]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page if page is not None else queryset, many=True)
        return success_response("FAQs retrieved.", data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            "FAQ created.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED,
        )


class FAQDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a FAQ."""

    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [IsAdminOrReadOnly]
    http_method_names = ["get", "patch", "delete"]

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return success_response("FAQ retrieved.", data=serializer.data)

    def partial_update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response("FAQ updated.", data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return success_response("FAQ deleted.", status_code=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------
class ContactCreateAPIView(generics.CreateAPIView):
    """Submit a contact form (public endpoint)."""

    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact = serializer.save()
        contact_services.notify_admin_of_contact(contact)
        return success_response(
            "Message sent successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED,
        )


class ContactListAPIView(generics.ListAPIView):
    """List all contact messages (admin only)."""

    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [IsAdmin]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page if page is not None else queryset, many=True)
        return success_response("Contact messages retrieved.", data=serializer.data)

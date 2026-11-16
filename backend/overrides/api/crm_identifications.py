from core.apps.crm import get_customer_identification_model
from core.apps.crm.api.serializers import CustomerIdentificationSerializer
from rest_framework import generics, permissions

CustomerIdentification = get_customer_identification_model()


class CustomerIdentificationListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomerIdentificationSerializer

    def get_queryset(self):
        return CustomerIdentification.available_objects.filter(
            customer__user=self.request.user
        ).select_related("customer")

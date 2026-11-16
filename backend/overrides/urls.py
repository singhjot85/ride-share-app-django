from rest_framework.routers import SimpleRouter

from overrides.api.document_views import UploadedDocumentViewSet

router = SimpleRouter()
router.register(
    r"document-uploads",
    UploadedDocumentViewSet,
    basename="document-upload",
)

urlpatterns = router.urls

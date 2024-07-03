from rest_framework.metadata import SimpleMetadata
from rest_framework.request import clone_request
from rest_framework import exceptions
from django.core.exceptions import PermissionDenied
from django.http import Http404


class CustomMetadata(SimpleMetadata):
    def determine_actions(self, request, view):
        """
        For generic class based views we return information about
        the fields that are accepted for 'PUT' and 'POST' methods.

        This method has been overridden to fix the AssertionError
        for OPTIONS call on list-view that accepts PUT as described
        at https://github.com/encode/django-rest-framework/issues/3356
        """
        actions = {}
        for method in {"PUT", "POST"} & set(view.allowed_methods):
            view.request = clone_request(request, method)
            try:
                # Test global permissions
                if hasattr(view, "check_permissions"):
                    view.check_permissions(view.request)
                # Test object permissions
                if method == "PUT" and hasattr(view, "get_object"):
                    # view_type has been added to the viewsets to determine
                    # if the viewset works with single or multiple objects.
                    # This check is skipped for viewset that works with
                    # multiple objects.
                    if (
                        hasattr(view, "view_type")
                        and getattr(view, "view_type") == "multiple_objects"
                    ):
                        pass
                    else:
                        view.get_object()

            except (exceptions.APIException, PermissionDenied, Http404):
                pass
            else:
                # If user has appropriate permissions for the view, include
                # appropriate metadata about the fields that should be supplied.
                serializer = view.get_serializer()
                actions[method] = self.get_serializer_info(serializer)
            finally:
                view.request = request

        return actions

from rest_framework.permissions import IsAuthenticated


class IsProfessor(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.get_role() == "professor"

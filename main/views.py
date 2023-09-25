from datetime import datetime

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import exceptions, status
from rest_framework.decorators import authentication_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from main.helpers import CustomPagination, Paginator
from main.models import ShoppingList
from main.serializer import (
    CreateAccountSerializer,
    LoginSerializer,
    ShoppingListModelSerializer,
    ShoppingListSerializer,
)

# error_codes = {
#     "40001": "User not found",
#     "40002": "Invalid input",
#     "40003": "Unauthorized access",
#     "40004": "Resource not found",
#     "40005": "Validation failed",
#     "40006": "Duplicate entry",
#     "40007": "Invalid request",
#     "40008": "Permission denied",
#     "40009": "Invalid token",
#     "40010": "Expired token"
# }


# Create your views here.
""" USER ACCOUNT SECTION """


class CreateAccountApiView(APIView):
    serializer_class = CreateAccountSerializer

    create_user_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "username": openapi.Schema(type=openapi.TYPE_STRING),
            "email": openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
            ),
            "password": openapi.Schema(type=openapi.TYPE_STRING),
            "confirm_password": openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=["username", "email", "password", "confirm_password"],
    )

    create_user_response_schema = {
        status.HTTP_400_BAD_REQUEST: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
        ),
        status.HTTP_201_CREATED: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "error": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                "code": openapi.Schema(type=openapi.TYPE_STRING),
                "tokens": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "refresh": openapi.Schema(type=openapi.TYPE_STRING),
                        "access": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            },
        ),
    }

    @method_decorator(csrf_exempt)
    @swagger_auto_schema(
        tags=["authentications"],
        request_body=create_user_schema,
        responses=create_user_response_schema,
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get("username")
        password = serializer.validated_data.get("password")
        email = serializer.validated_data.get("email")

        User = get_user_model()

        # check if user email or username already exists
        if User.objects.filter(email=email).exists():
            raise exceptions.ValidationError({"email": "Email already exists"})
        elif User.objects.filter(username=username).exists():
            raise exceptions.ValidationError({"username": "Username already exists"})
        else:
            user = User.objects.create(
                username=username, password=make_password(password), email=email
            )
            user.save()

            tokenr = TokenObtainPairSerializer().get_token(user)
            tokena = AccessToken().for_user(user)

            data = {
                "error": False,
                "code": "201",
            }

            data["tokens"] = {"refresh": str(tokenr), "access": str(tokena)}

            return Response(data, status=status.HTTP_201_CREATED)


class LoginApiView(APIView):
    serilaier_class = LoginSerializer

    login_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "username_or_email": openapi.Schema(type=openapi.TYPE_STRING),
            "password": openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=["username_or_email", "password"],
    )

    login_response_schema = {
        status.HTTP_400_BAD_REQUEST: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "error": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                "code": openapi.Schema(type=openapi.TYPE_STRING),
                "message": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "error": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                "code": openapi.Schema(type=openapi.TYPE_STRING),
                "tokens": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "refresh": openapi.Schema(type=openapi.TYPE_STRING),
                        "access": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            },
        ),
    }

    @method_decorator(csrf_exempt)
    @swagger_auto_schema(
        tags=["authentications"],
        request_body=login_schema,
        responses=login_response_schema,
    )
    def post(self, request):
        serilaizer = self.serilaier_class(data=request.data)
        serilaizer.is_valid(raise_exception=True)

        username_or_email = serilaizer.validated_data.get("username_or_email")
        password = serilaizer.validated_data.get("password")

        try:
            user = authenticate(email=username_or_email, password=password)
        except Exception as e:
            data = {
                "error": True,
                "code": "40001",
                "message": str(e),
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        tokenr = TokenObtainPairSerializer().get_token(user)
        tokena = AccessToken().for_user(user)

        data = {
            "error": False,
            "code": "200",
        }

        data["tokens"] = {"refresh": str(tokenr), "access": str(tokena)}

        return Response(data, status=status.HTTP_200_OK)


""" END OF USER ACCOUNT SECTION """


""" SHOPPING LIST SECTION """


class ShoppingListApiView(APIView, Paginator):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    serializer_class = ShoppingListSerializer

    pagination_class = CustomPagination

    create_shopping_list_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "name": openapi.Schema(type=openapi.TYPE_STRING),
            "quantity": openapi.Schema(type=openapi.TYPE_INTEGER),
            "note": openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=["name", "quantity"],
    )

    create_shopping_list_response_schema = {
        status.HTTP_400_BAD_REQUEST: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "error": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                "code": openapi.Schema(type=openapi.TYPE_STRING),
                "message": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        status.HTTP_201_CREATED: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "error": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                "code": openapi.Schema(type=openapi.TYPE_STRING),
                "message": openapi.Schema(type=openapi.TYPE_STRING),
                "data": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "name": openapi.Schema(type=openapi.TYPE_STRING),
                        "quantity": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "note": openapi.Schema(type=openapi.TYPE_STRING),
                        "created_at": openapi.Schema(type=openapi.TYPE_STRING),
                        "updated_at": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            },
        ),
    }

    @method_decorator(csrf_exempt)
    @swagger_auto_schema(
        tags=["shopping-list"],
        request_body=create_shopping_list_schema,
        responses=create_shopping_list_response_schema,
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        create_shopping_list_payload = {
            "user": request.user,
            "name": serializer.validated_data.get("name"),
            "quantity": serializer.validated_data.get("quantity"),
            "note": serializer.validated_data.get("note"),
        }

        shopping_list = ShoppingList.create_shopping_list(
            **create_shopping_list_payload
        )

        data = {
            "error": False,
            "code": "201",
            "message": "Shopping list created successfully",
            "data": ShoppingListModelSerializer(shopping_list).data,
        }

        return Response(data, status=status.HTTP_201_CREATED)

    @method_decorator(csrf_exempt)
    @swagger_auto_schema(
        tags=["shopping-list"],
    )
    def get(self, request):
        sort_by = request.GET.get("sort_by")
        search = request.GET.get("search")
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        sort_options = ["asc", "desc"]

        if sort_by and sort_by not in sort_options:
            data = {
                "error": True,
                "code": "40007",
                "message": "Invalid sort option",
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if start_date and not end_date:
            data = {
                "error": True,
                "code": "40007",
                "message": "End date is required",
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if end_date and not start_date:
            data = {
                "error": True,
                "code": "40007",
                "message": "Start date is required",
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if start_date and end_date:
            # formate date
            try:
                if start_date:
                    datetime.strptime(start_date, "%Y-%m-%d")
                if end_date:
                    datetime.strptime(end_date, "%Y-%m-%d")
            except:
                data = {
                    "error": True,
                    "code": "40007",
                    "message": "Invalid date format. Date format should be YYYY-MM-DD",
                }

                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        if start_date and end_date:
            shopping_list = ShoppingList.filter_by_date(
                user_id=request.user.id, start_date=start_date, end_date=end_date
            )
        elif search:
            shopping_list = ShoppingList.search_shopping_list(request.user.id, search)
        else:
            shopping_list = ShoppingList.get_shopping_list(request.user.id)

        if sort_by:
            shopping_list = ShoppingList.sort_data(shopping_list, sort_by)

        paginator = PageNumberPagination()
        paginator.page_size = 10

        result_page = paginator.paginate_queryset(shopping_list, request)

        serialized_data = ShoppingListModelSerializer(result_page, many=True).data

        data = {
            "error": False,
            "code": "200",
            "message": "Shopping list retrieved successfully",
            "data": serialized_data,
        }

        return paginator.get_paginated_response(data)

    def patch(self, request):
        item_id = request.GET.get("item_id")
        if not item_id:
            data = {
                "error": True,
                "code": "40007",
                "message": "Item id is required",
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        shopping_list = ShoppingList.get_shopping_list_by_id(request.user.id, item_id)

        if shopping_list is None:
            data = {
                "error": True,
                "code": "40004",
                "message": "Shopping list does not exist",
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        name = request.data.get("name", shopping_list.name)
        quantity = request.data.get("quantity", shopping_list.quantity)
        note = request.data.get("note", shopping_list.note)

        shopping_list.name = name
        shopping_list.quantity = quantity
        shopping_list.note = note
        shopping_list.save()

        data = {
            "error": False,
            "code": "200",
            "message": "Shopping list retrieved successfully",
            "data": ShoppingListModelSerializer(shopping_list).data,
        }

        return Response(data, status=status.HTTP_200_OK)

    def put(self, request):
        serilaizer = self.serializer_class(data=request.data)
        serilaizer.is_valid(raise_exception=True)

        item_id = request.GET.get("item_id")
        if not item_id:
            data = {
                "error": True,
                "code": "40007",
                "message": "Item id is required",
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        shopping_list = ShoppingList.get_shopping_list_by_id(request.user.id, item_id)

        if shopping_list is None:
            data = {
                "error": True,
                "code": "40004",
                "message": "Shopping list does not exist",
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        shopping_list.name = serilaizer.validated_data.get("name")
        shopping_list.quantity = serilaizer.validated_data.get("quantity")
        shopping_list.note = serilaizer.validated_data.get("note")
        shopping_list.save()

        data = {
            "error": False,
            "code": "200",
            "message": "Shopping list retrieved successfully",
            "data": ShoppingListModelSerializer(shopping_list).data,
        }

        return Response(data, status=status.HTTP_200_OK)

    def delete(self, request):
        item_id = request.GET.get("item_id")
        if not item_id:
            data = {
                "error": True,
                "code": "40007",
                "message": "Item id is required",
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        shopping_list = ShoppingList.get_shopping_list_by_id(request.user.id, item_id)

        if shopping_list is None:
            data = {
                "error": True,
                "code": "40004",
                "message": "Shopping list does not exist",
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        shopping_list.is_deleted = True
        shopping_list.save()

        data = {
            "error": False,
            "code": "200",
            "message": "Shopping list deleted successfully",
        }

        return Response(data, status=status.HTTP_200_OK)


""" END OF SHOPPING LIST SECTION """

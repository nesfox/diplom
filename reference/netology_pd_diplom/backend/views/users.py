from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.models import Token
from backend.models import ConfirmEmailToken, Contact
from backend.serializers import UserSerializer, ContactSerializer


class RegisterAccount(APIView):
    def post(self, request, *args, **kwargs):
        if {
            'first_name',
            'last_name',
            'email',
            'password',
            'company',
            'position'
        }.issubset(request.data):
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                return Response(
                    {'Status': False, 'Errors': {'password': password_error}},
                    status=400
                )

            user_serializer = UserSerializer(data=request.data)
            if user_serializer.is_valid():
                user = user_serializer.save()
                user.set_password(request.data['password'])
                user.save()
                return Response({'Status': True})
            return Response(
                {'Status': False, 'Errors': user_serializer.errors},
                status=400
            )
        return Response(
            {
                'Status': False,
                'Errors': 'Не указаны все необходимые аргументы'
            },
            status=400
        )


class ConfirmAccount(APIView):
    def post(self, request, *args, **kwargs):
        if {'email', 'token'}.issubset(request.data):
            token = ConfirmEmailToken.objects.filter(
                user__email=request.data['email'],
                key=request.data['token']
            ).first()
            if token:
                token.user.is_active = True
                token.user.save()
                token.delete()
                return Response({'Status': True})
            return Response(
                {'Status': False, 'Errors': 'Неправильный токен или email'},
                status=400
            )
        return Response(
            {
                'Status': False,
                'Errors': 'Не указаны все необходимые аргументы'
            },
            status=400
        )


class LoginAccount(APIView):
    def post(self, request, *args, **kwargs):
        if {'email', 'password'}.issubset(request.data):
            user = authenticate(
                request,
                username=request.data['email'],
                password=request.data['password']
            )

            if user and user.is_active:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'Status': True, 'Token': token.key})
            return Response(
                {'Status': False, 'Errors': 'Не удалось авторизовать'},
                status=400
            )
        return Response(
            {
                'Status': False,
                'Errors': 'Не указаны все необходимые аргументы'
            },
            status=400
        )


class AccountDetails(APIView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Log in required'},
                status=403
            )
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Log in required'},
                status=403
            )

        if 'password' in request.data:
            try:
                validate_password(request.data['password'])
                request.user.set_password(request.data['password'])
            except Exception as password_error:
                return Response(
                    {'Status': False, 'Errors': {'password': password_error}},
                    status=400
                )

        user_serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({'Status': True})
        return Response(
            {'Status': False, 'Errors': user_serializer.errors},
            status=400
        )


class ContactView(APIView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Log in required'},
                status=403
            )
        contact = Contact.objects.filter(user_id=request.user.id)
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Log in required'},
                status=403
            )

        if {'city', 'street', 'phone'}.issubset(request.data):
            request.data._mutable = True
            request.data.update({'user': request.user.id})
            serializer = ContactSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response({'Status': True})
            return Response(
                {'Status': False, 'Errors': serializer.errors},
                status=400
            )
        return Response(
            {
                'Status': False,
                'Errors': 'Не указаны все необходимые аргументы'
            },
            status=400
        )

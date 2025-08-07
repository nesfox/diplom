from drf_spectacular.utils import (
    inline_serializer,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes
)
from rest_framework import serializers
from backend.serializers import OrderSerializer
from drf_spectacular.extensions import OpenApiViewExtension


class StatusSerializer(serializers.Serializer):
    status = serializers.BooleanField()
    errors = serializers.CharField()


class StatusAuthErrSerializer(serializers.Serializer):
    status = serializers.BooleanField()
    error = serializers.CharField(default='Log in required')


class NewTaskSerializer(serializers.Serializer):
    status = serializers.BooleanField()
    task_id = serializers.CharField()


class ItemSerializer(serializers.Serializer):
    product_info = serializers.IntegerField()
    quantity = serializers.IntegerField()


class ItemsSerializer(serializers.Serializer):
    items = ItemSerializer(many=True)


class ItemUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    quantity = serializers.IntegerField()


class ItemsUpdateSerializer(serializers.Serializer):
    items = ItemUpdateSerializer(many=True)


class ConfirmEmailSerializer(serializers.Serializer):
    email = serializers.CharField()
    token = serializers.CharField()


class OrderViewSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    contact = serializers.IntegerField()


class FixRegisterAccount(OpenApiViewExtension):
    target_class = 'backend.views.RegisterAccount'

    def view_replacement(self):
        @extend_schema(
            tags=['Users'],
            summary='Register new account',
            request=inline_serializer(
                name='RegisterAccountRequest',
                fields={
                    'first_name': serializers.CharField(),
                    'last_name': serializers.CharField(),
                    'email': serializers.CharField(),
                    'password': serializers.CharField(),
                    'company': serializers.CharField(),
                    'position': serializers.CharField(),
                },
            ),
            responses={200: StatusSerializer},
        )
        class FixedRegisterAccount(self.target_class):
            pass
        return FixedRegisterAccount


class FixLoginAccount(OpenApiViewExtension):
    target_class = 'backend.views.LoginAccount'

    def view_replacement(self):
        @extend_schema(
            tags=['Users'],
            summary='Login to account',
            request=inline_serializer(
                name='LoginAccountRequest',
                fields={
                    'email': serializers.CharField(),
                    'password': serializers.CharField(),
                },
            ),
            responses={
                200: inline_serializer(
                    name='LoginAccountResponseOk',
                    fields={
                        'status': serializers.BooleanField(),
                        'token': serializers.CharField(),
                    },
                ),
            },
        )
        class FixedLoginAccount(self.target_class):
            pass
        return FixedLoginAccount


class FixBasketView(OpenApiViewExtension):
    target_class = 'backend.views.BasketView'

    def view_replacement(self):
        @extend_schema(
            tags=['Shop'],
            summary='User basket',
            responses={
                200: OrderSerializer,
                403: StatusAuthErrSerializer,
            },
        )
        class FixedBasketView(self.target_class):
            @extend_schema(
                summary='Get basket items',
                responses={
                    200: OrderSerializer,
                    403: StatusAuthErrSerializer,
                },
            )
            def get(self, request, *args, **kwargs):
                pass

            @extend_schema(
                summary='Add item to basket',
                request=ItemsSerializer,
                responses={
                    200: inline_serializer(
                        name='BasketAddResponse',
                        fields={
                            'status': serializers.BooleanField(),
                            'created': serializers.CharField(),
                        },
                    ),
                    403: StatusAuthErrSerializer,
                },
            )
            def post(self, request, *args, **kwargs):
                pass

            @extend_schema(
                summary='Update basket item',
                request=ItemsUpdateSerializer,
                responses={
                    200: inline_serializer(
                        name='BasketUpdateResponse',
                        fields={
                            'status': serializers.BooleanField(),
                            'updated': serializers.CharField(),
                        },
                    ),
                    403: StatusAuthErrSerializer,
                },
            )
            def put(self, request, *args, **kwargs):
                pass

            @extend_schema(
                summary='Remove item from basket',
                request=ItemsSerializer,
                responses={
                    200: inline_serializer(
                        name='BasketDeleteResponse',
                        fields={
                            'status': serializers.BooleanField(),
                            'deleted': serializers.CharField(),
                        },
                    ),
                },
            )
            def delete(self, request, *args, **kwargs):
                pass
        
        return FixedBasketView


class FixPartnerExport(OpenApiViewExtension):
    target_class = 'backend.views.PartnerExport'

    def view_replacement(self):
        @extend_schema(
            tags=['Partner'],
            summary='Export partner price list',
            responses={
                200: inline_serializer(
                    name='PartnerExportResponse',
                    fields={
                        'status': serializers.BooleanField(),
                        'task_id': serializers.CharField(),
                        'url': serializers.CharField(),
                    },
                ),
            },
        )
        class FixedPartnerExport(self.target_class):
            pass
        return FixedPartnerExport


class FixPartnerOrders(OpenApiViewExtension):
    target_class = 'backend.views.PartnerOrders'

    def view_replacement(self):
        @extend_schema(tags=['Partner'])
        class FixedPartnerOrders(self.target_class):
            @extend_schema(
                summary='Get partner orders',
                responses={200: OrderSerializer},
            )
            def get(self, request, *args, **kwargs):
                pass
            
            @extend_schema(
                summary='Update order status',
                responses={200: StatusSerializer},
            )
            def put(self, request, *args, **kwargs):
                pass

        return FixedPartnerOrders


class FixResultsView(OpenApiViewExtension):
    target_class = 'backend.views.ResultsView'

    def view_replacement(self):
        @extend_schema(
            tags=['Common'],
            summary='Get async task result',
            responses={
                200: inline_serializer(
                    name='TaskResultResponse',
                    fields={
                        'status': serializers.BooleanField(),
                        'result': serializers.CharField(),
                    },
                ),
            },
        )
        class FixedResultsView(self.target_class):
            def get(self, request, *args, **kwargs):
                pass

        return FixedResultsView

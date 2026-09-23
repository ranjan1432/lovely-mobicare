from decimal import Decimal

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import RequestFactory
from django.urls import reverse

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from products.models import Product
from orders.admin import OrderAdmin
from orders.models import Order, OrderItem

from unittest.mock import MagicMock, patch


# =========================================================
# ORDER CREATION TESTS
# =========================================================

class OrderAPITests(APITestCase):

    def setUp(self):
        self.order_url = reverse("order-create")

        # -------------------------------------------------
        # TEST USER
        # -------------------------------------------------

        self.user = User.objects.create_user(
            username="customer@example.com",
            email="customer@example.com",
            password="TestPassword123!",
            first_name="Test",
            last_name="Customer",
        )

        self.token = Token.objects.create(
            user=self.user
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Token {self.token.key}"
            )
        )

        # -------------------------------------------------
        # TEST PRODUCT
        # -------------------------------------------------

        self.product = Product.objects.create(
            name="Test Charger",
            description="Test product",
            price=Decimal("499.00"),
            stock=10,
            is_active=True,
        )

        # -------------------------------------------------
        # VALID ORDER PAYLOAD
        # -------------------------------------------------

        self.valid_order_data = {
            "customer_name": "Test Customer",
            "email": "test@example.com",
            "phone": "9876543210",
            "address": "123 Test Street, Erode",
            "city": "Erode",
            "postal_code": "638001",
            "payment_method": "cod",
            "items": [
                {
                    "product_id": self.product.id,
                    "quantity": 2,
                }
            ],
        }

    # =====================================================
    # AUTHENTICATION
    # =====================================================

    def test_unauthenticated_user_cannot_create_order(self):
        self.client.credentials()

        response = self.client.post(
            self.order_url,
            self.valid_order_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertEqual(
            Order.objects.count(),
            0,
        )

    # =====================================================
    # SUCCESSFUL ORDER
    # =====================================================

    def test_create_order_successfully(self):
        response = self.client.post(
            self.order_url,
            self.valid_order_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        order = Order.objects.get()

        self.assertEqual(
            order.total_amount,
            Decimal("998.00"),
        )

    # =====================================================
    # ORDER OWNERSHIP
    # =====================================================

    def test_created_order_belongs_to_logged_in_user(self):
        response = self.client.post(
            self.order_url,
            self.valid_order_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        order = Order.objects.get()

        self.assertEqual(
            order.user,
            self.user,
        )

    # =====================================================
    # PRICE / TOTAL SECURITY
    # =====================================================

    def test_client_cannot_manipulate_total_amount(self):
        data = self.valid_order_data.copy()

        data["total_amount"] = "1.00"

        response = self.client.post(
            self.order_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        order = Order.objects.get()

        self.assertEqual(
            order.total_amount,
            Decimal("998.00"),
        )

    # =====================================================
    # PHONE VALIDATION
    # =====================================================

    def test_invalid_phone_is_rejected(self):
        data = self.valid_order_data.copy()

        data["phone"] = "12345"

        response = self.client.post(
            self.order_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Order.objects.count(),
            0,
        )

    # =====================================================
    # COD CITY VALIDATION
    # =====================================================

    def test_invalid_cod_city_is_rejected(self):
        data = self.valid_order_data.copy()

        data["city"] = "Chennai"

        response = self.client.post(
            self.order_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Order.objects.count(),
            0,
        )

    # =====================================================
    # STOCK VALIDATION
    # =====================================================

    def test_insufficient_stock_is_rejected(self):
        data = self.valid_order_data.copy()

        data["items"] = [
            {
                "product_id": self.product.id,
                "quantity": 50,
            }
        ]

        response = self.client.post(
            self.order_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Order.objects.count(),
            0,
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            10,
        )

    def test_successful_order_decreases_product_stock(self):
        response = self.client.post(
            self.order_url,
            self.valid_order_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            8,
        )

    # =====================================================
    # TRANSACTION ROLLBACK
    # =====================================================

    def test_duplicate_product_over_stock_rolls_back_order(self):
        data = self.valid_order_data.copy()

        data["items"] = [
            {
                "product_id": self.product.id,
                "quantity": 6,
            },
            {
                "product_id": self.product.id,
                "quantity": 6,
            },
        ]

        response = self.client.post(
            self.order_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Order.objects.count(),
            0,
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            10,
        )


# =========================================================
# MY ORDERS AUTHENTICATED API TESTS
# =========================================================

class MyOrdersAPITests(APITestCase):

    def setUp(self):
        self.my_orders_url = reverse("my-orders")

        # -------------------------------------------------
        # USER A
        # -------------------------------------------------

        self.user_a = User.objects.create_user(
            username="usera@example.com",
            email="usera@example.com",
            password="TestPassword123!",
            first_name="User",
            last_name="A",
        )

        self.token_a = Token.objects.create(
            user=self.user_a
        )

        # -------------------------------------------------
        # USER B
        # -------------------------------------------------

        self.user_b = User.objects.create_user(
            username="userb@example.com",
            email="userb@example.com",
            password="TestPassword123!",
            first_name="User",
            last_name="B",
        )

        self.token_b = Token.objects.create(
            user=self.user_b
        )

        # -------------------------------------------------
        # USER A ORDERS
        # -------------------------------------------------

        self.order_a1 = Order.objects.create(
            user=self.user_a,
            customer_name="User A",
            email="usera@example.com",
            phone="9876543210",
            address="123 Test Street, Erode",
            city="Erode",
            postal_code="638001",
            status="pending",
            total_amount=Decimal("499.00"),
            payment_method="cod",
        )

        self.order_a2 = Order.objects.create(
            user=self.user_a,
            customer_name="User A",
            email="usera@example.com",
            phone="9876543210",
            address="456 Test Street, Erode",
            city="Erode",
            postal_code="638001",
            status="completed",
            total_amount=Decimal("999.00"),
            payment_method="cod",
        )

        # -------------------------------------------------
        # USER B ORDER
        # -------------------------------------------------

        self.order_b = Order.objects.create(
            user=self.user_b,
            customer_name="User B",
            email="userb@example.com",
            phone="9876543211",
            address="789 Test Street, Erode",
            city="Erode",
            postal_code="638001",
            status="processing",
            total_amount=Decimal("1499.00"),
            payment_method="cod",
        )

    # =====================================================
    # LOGIN REQUIRED
    # =====================================================

    def test_unauthenticated_user_cannot_view_my_orders(self):
        response = self.client.get(
            self.my_orders_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # =====================================================
    # USER CAN VIEW OWN ORDERS
    # =====================================================

    def test_logged_in_user_can_view_own_orders(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Token {self.token_a.key}"
            )
        )

        response = self.client.get(
            self.my_orders_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            2,
        )

        returned_ids = {
            order["id"]
            for order in response.data
        }

        self.assertIn(
            self.order_a1.id,
            returned_ids,
        )

        self.assertIn(
            self.order_a2.id,
            returned_ids,
        )

    # =====================================================
    # USER CANNOT VIEW OTHER USER'S ORDERS
    # =====================================================

    def test_my_orders_does_not_expose_other_users_orders(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Token {self.token_a.key}"
            )
        )

        response = self.client.get(
            self.my_orders_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = {
            order["id"]
            for order in response.data
        }

        self.assertNotIn(
            self.order_b.id,
            returned_ids,
        )

    # =====================================================
    # PRIVATE DETAILS NOT EXPOSED
    # =====================================================

    def test_my_orders_does_not_expose_private_details(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Token {self.token_a.key}"
            )
        )

        response = self.client.get(
            self.my_orders_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertGreater(
            len(response.data),
            0,
        )

        first_order = response.data[0]

        self.assertNotIn(
            "phone",
            first_order,
        )

        self.assertNotIn(
            "email",
            first_order,
        )

        self.assertNotIn(
            "address",
            first_order,
        )

        self.assertNotIn(
            "postal_code",
            first_order,
        )


# =========================================================
# PUBLIC ORDER TRACKING TESTS
# =========================================================

class OrderTrackingAPITests(APITestCase):

    def setUp(self):
        self.tracking_url = reverse(
            "order-track"
        )

        self.order = Order.objects.create(
            customer_name="Tracking Customer",
            email="tracking@example.com",
            phone="9876543210",
            address="123 Test Street, Erode",
            city="Erode",
            postal_code="638001",
            status="pending",
            total_amount=Decimal("499.00"),
            payment_method="cod",
        )

    # =====================================================
    # CORRECT TRACKING DETAILS
    # =====================================================

    def test_tracking_with_correct_order_id_and_phone(self):
        response = self.client.post(
            self.tracking_url,
            {
                "order_id": self.order.id,
                "phone": "9876543210",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.order.id,
        )

    # =====================================================
    # WRONG PHONE
    # =====================================================

    def test_tracking_with_wrong_phone_is_rejected(self):
        response = self.client.post(
            self.tracking_url,
            {
                "order_id": self.order.id,
                "phone": "9876543211",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # =====================================================
    # INVALID PHONE
    # =====================================================

    def test_invalid_tracking_phone_is_rejected(self):
        response = self.client.post(
            self.tracking_url,
            {
                "order_id": self.order.id,
                "phone": "12345",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # =====================================================
    # TRACKING PRIVACY
    # =====================================================

    def test_tracking_response_does_not_expose_private_details(self):
        response = self.client.post(
            self.tracking_url,
            {
                "order_id": self.order.id,
                "phone": "9876543210",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertNotIn(
            "phone",
            response.data,
        )

        self.assertNotIn(
            "email",
            response.data,
        )

        self.assertNotIn(
            "address",
            response.data,
        )

        self.assertNotIn(
            "postal_code",
            response.data,
        )

# =========================================================
# ORDER CANCELLATION / STOCK RESTORE TESTS
# =========================================================

class OrderCancellationStockTests(APITestCase):

    def setUp(self):
        # -------------------------------------------------
        # PRODUCT
        #
        # Original stock was 10.
        # This test starts at 8 to simulate an order that
        # has already deducted 2 units.
        # -------------------------------------------------

        self.product = Product.objects.create(
            name="Cancellation Test Charger",
            description=(
                "Cancellation stock test product"
            ),
            price=Decimal("499.00"),
            stock=8,
            is_active=True,
        )

        # -------------------------------------------------
        # COD ORDER
        #
        # Stock has already been deducted for this order,
        # therefore stock_deducted MUST be True.
        # -------------------------------------------------

        self.order = Order.objects.create(
            customer_name="Cancel Customer",
            email="cancel@example.com",
            phone="9876543210",
            address="123 Test Street, Erode",
            city="Erode",
            postal_code="638001",
            status="pending",
            total_amount=Decimal("998.00"),
            payment_method="cod",
            payment_status="pending",
            stock_deducted=True,
            stock_restored=False,
        )

        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            product_name=self.product.name,
            price=self.product.price,
            quantity=2,
        )

        self.site = AdminSite()

        self.order_admin = OrderAdmin(
            Order,
            self.site,
        )

        self.request = RequestFactory().post(
            "/admin/orders/order/"
        )

    # =====================================================
    # CANCELLED ORDER RESTORES PRODUCT STOCK
    # =====================================================

    def test_cancelled_order_restores_product_stock(self):
        self.order.status = "cancelled"

        self.order_admin.save_model(
            self.request,
            self.order,
            form=None,
            change=True,
        )

        restored = (
            self.order_admin
            .restore_cancelled_order_stock(
                self.order.pk
            )
        )

        self.product.refresh_from_db()
        self.order.refresh_from_db()

        self.assertTrue(
            restored
        )

        # Stock was 8 after deduction.
        # Cancellation restores the 2 units.
        self.assertEqual(
            self.product.stock,
            10,
        )

        self.assertTrue(
            self.order.stock_deducted,
        )

        self.assertTrue(
            self.order.stock_restored,
        )

    # =====================================================
    # STOCK CANNOT BE RESTORED TWICE
    # =====================================================

    def test_cancelled_order_does_not_restore_stock_twice(self):
        self.order.status = "cancelled"

        self.order_admin.save_model(
            self.request,
            self.order,
            form=None,
            change=True,
        )

        first_restore = (
            self.order_admin
            .restore_cancelled_order_stock(
                self.order.pk
            )
        )

        second_restore = (
            self.order_admin
            .restore_cancelled_order_stock(
                self.order.pk
            )
        )

        self.product.refresh_from_db()
        self.order.refresh_from_db()

        self.assertTrue(
            first_restore
        )

        self.assertFalse(
            second_restore
        )

        # Must remain 10.
        # It must NOT become 12.
        self.assertEqual(
            self.product.stock,
            10,
        )

        self.assertTrue(
            self.order.stock_restored,
        )

    # =====================================================
    # ACTIVE ORDER MUST NOT RESTORE STOCK
    # =====================================================

    def test_active_order_does_not_restore_stock(self):
        restored = (
            self.order_admin
            .restore_cancelled_order_stock(
                self.order.pk
            )
        )

        self.product.refresh_from_db()
        self.order.refresh_from_db()

        self.assertFalse(
            restored
        )

        # Order is still active, so deducted stock stays 8.
        self.assertEqual(
            self.product.stock,
            8,
        )

        self.assertFalse(
            self.order.stock_restored,
        )

    # =====================================================
    # UNPAID ONLINE ORDER MUST NOT RESTORE STOCK
    #
    # CRITICAL REGRESSION TEST:
    #
    # Razorpay pending order does NOT deduct stock.
    # Therefore cancelling it must NOT add stock.
    # =====================================================

    def test_unpaid_online_order_does_not_restore_stock(self):
        online_product = Product.objects.create(
            name="Pending Online Charger",
            slug="pending-online-charger",
            description=(
                "Pending online payment test product"
            ),
            price=Decimal("499.00"),
            stock=10,
            is_active=True,
        )

        online_order = Order.objects.create(
            customer_name="Online Customer",
            email="online@example.com",
            phone="9876543211",
            address="456 Online Street, Chennai",
            city="Chennai",
            postal_code="600001",
            status="cancelled",
            total_amount=Decimal("998.00"),
            payment_method="online",
            payment_status="pending",
            stock_deducted=False,
            stock_restored=False,
            razorpay_order_id=(
                "order_pending_cancel_test"
            ),
        )

        OrderItem.objects.create(
            order=online_order,
            product=online_product,
            product_name=online_product.name,
            price=online_product.price,
            quantity=2,
        )

        restored = (
            self.order_admin
            .restore_cancelled_order_stock(
                online_order.pk
            )
        )

        online_product.refresh_from_db()
        online_order.refresh_from_db()

        self.assertFalse(restored)

        # Stock was never deducted, so cancellation
        # must not increase it to 12.
        self.assertEqual(
            online_product.stock,
            10,
        )

        self.assertFalse(
            online_order.stock_deducted,
        )

        self.assertFalse(
            online_order.stock_restored,
        )

    # =====================================================
    # CANCELLED ORDER CANNOT BECOME ACTIVE AGAIN
    # =====================================================

    def test_cancelled_order_cannot_be_reactivated(self):
        self.order.status = "cancelled"
        self.order.stock_restored = True

        self.order.save(
            update_fields=[
                "status",
                "stock_restored",
            ]
        )

        self.order.status = "processing"

        with self.assertRaises(
            ValidationError
        ):
            self.order_admin.save_model(
                self.request,
                self.order,
                form=None,
                change=True,
            )

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            "cancelled",
        )

        # =========================================================
# RAZORPAY PAYMENT TESTS
# =========================================================

class RazorpayPaymentAPITests(APITestCase):

    def setUp(self):
        self.create_url = reverse(
            "razorpay-create-order"
        )

        self.verify_url = reverse(
            "razorpay-verify-payment"
        )

        # -------------------------------------------------
        # TEST USER
        # -------------------------------------------------

        self.user = User.objects.create_user(
            username="razorpay@example.com",
            email="razorpay@example.com",
            password="TestPassword123!",
            first_name="Razorpay",
            last_name="Customer",
        )

        self.token = Token.objects.create(
            user=self.user
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Token {self.token.key}"
            )
        )

        # -------------------------------------------------
        # TEST PRODUCT
        # -------------------------------------------------

        self.product = Product.objects.create(
            name="Razorpay Test Charger",
            description="Razorpay test product",
            price=Decimal("499.00"),
            stock=10,
            is_active=True,
        )

        # -------------------------------------------------
        # VALID ONLINE PAYMENT PAYLOAD
        # -------------------------------------------------

        self.valid_payment_data = {
            "customer_name": "Razorpay Customer",
            "email": "razorpay@example.com",
            "phone": "9876543210",
            "address": "123 Online Payment Street",
            "city": "Chennai",
            "postal_code": "600001",
            "items": [
                {
                    "product_id": self.product.id,
                    "quantity": 2,
                }
            ],
        }

    # =====================================================
    # HELPERS
    # =====================================================

    def create_pending_online_order(
        self,
        razorpay_order_id="order_test_123",
    ):
        order = Order.objects.create(
            user=self.user,
            customer_name="Razorpay Customer",
            email="razorpay@example.com",
            phone="9876543210",
            address="123 Online Payment Street",
            city="Chennai",
            postal_code="600001",
            status="pending",
            total_amount=Decimal("998.00"),
            payment_method="online",
            payment_status="pending",
            razorpay_order_id=razorpay_order_id,
        )

        OrderItem.objects.create(
            order=order,
            product=self.product,
            product_name=self.product.name,
            price=self.product.price,
            quantity=2,
        )

        return order

    def valid_fetched_payment(
        self,
        order,
        payment_id="pay_test_123",
    ):
        return {
            "id": payment_id,
            "order_id": order.razorpay_order_id,
            "amount": 99800,
            "currency": "INR",
            "status": "captured",
            "captured": True,
        }

    # =====================================================
    # CREATE - LOGIN REQUIRED
    # =====================================================

    def test_unauthenticated_user_cannot_create_razorpay_order(
        self
    ):
        self.client.credentials()

        response = self.client.post(
            self.create_url,
            self.valid_payment_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertEqual(
            Order.objects.count(),
            0,
        )

    # =====================================================
    # CREATE - BACKEND CALCULATES AMOUNT
    # =====================================================

    @patch("orders.views.razorpay.Client")
    def test_razorpay_create_uses_database_price(
        self,
        mock_client_class,
    ):
        mock_client = MagicMock()

        mock_client.order.create.return_value = {
            "id": "order_test_create_123",
            "amount": 99800,
            "currency": "INR",
        }

        mock_client_class.return_value = (
            mock_client
        )

        data = self.valid_payment_data.copy()

        # Fake frontend values must not affect backend total.
        data["total_amount"] = "1.00"
        data["amount"] = 100

        response = self.client.post(
            self.create_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["amount"],
            99800,
        )

        self.assertEqual(
            response.data["total_amount"],
            "998.00",
        )

        order = Order.objects.get()

        self.assertEqual(
            order.total_amount,
            Decimal("998.00"),
        )

        self.assertEqual(
            order.payment_method,
            "online",
        )

        self.assertEqual(
            order.payment_status,
            "pending",
        )

        self.assertEqual(
            order.razorpay_order_id,
            "order_test_create_123",
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            10,
        )

        mock_client.order.create.assert_called_once_with(
            {
                "amount": 99800,
                "currency": "INR",
                "payment_capture": 1,
            }
        )

    # =====================================================
    # CREATE - LOCAL ORDER BELONGS TO USER
    # =====================================================

    @patch("orders.views.razorpay.Client")
    def test_razorpay_create_order_belongs_to_logged_in_user(
        self,
        mock_client_class,
    ):
        mock_client = MagicMock()

        mock_client.order.create.return_value = {
            "id": "order_test_owner_123",
        }

        mock_client_class.return_value = (
            mock_client
        )

        response = self.client.post(
            self.create_url,
            self.valid_payment_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        order = Order.objects.get()

        self.assertEqual(
            order.user,
            self.user,
        )

    # =====================================================
    # CREATE - ORDER ITEMS SAVED SERVER-SIDE
    # =====================================================

    @patch("orders.views.razorpay.Client")
    def test_razorpay_create_saves_order_items(
        self,
        mock_client_class,
    ):
        mock_client = MagicMock()

        mock_client.order.create.return_value = {
            "id": "order_test_items_123",
        }

        mock_client_class.return_value = (
            mock_client
        )

        response = self.client.post(
            self.create_url,
            self.valid_payment_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        order = Order.objects.get()

        item = order.items.get()

        self.assertEqual(
            item.product,
            self.product,
        )

        self.assertEqual(
            item.product_name,
            self.product.name,
        )

        self.assertEqual(
            item.price,
            Decimal("499.00"),
        )

        self.assertEqual(
            item.quantity,
            2,
        )

    # =====================================================
    # VERIFY - LOGIN REQUIRED
    # =====================================================

    def test_unauthenticated_user_cannot_verify_payment(
        self
    ):
        self.client.credentials()

        response = self.client.post(
            self.verify_url,
            {
                "razorpay_order_id": "order_test_123",
                "razorpay_payment_id": "pay_test_123",
                "razorpay_signature": "signature",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # =====================================================
    # VERIFY - INVALID SIGNATURE
    # =====================================================

    @patch("orders.views.razorpay.Client")
    def test_invalid_razorpay_signature_is_rejected(
        self,
        mock_client_class,
    ):
        order = (
            self.create_pending_online_order()
        )

        mock_client = MagicMock()

        mock_client.utility.verify_payment_signature.side_effect = (
            Exception("Invalid signature")
        )

        mock_client_class.return_value = (
            mock_client
        )

        response = self.client.post(
            self.verify_url,
            {
                "razorpay_order_id": (
                    order.razorpay_order_id
                ),
                "razorpay_payment_id": (
                    "pay_invalid_123"
                ),
                "razorpay_signature": (
                    "invalid_signature"
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        mock_client.payment.fetch.assert_not_called()

        order.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(
            order.payment_status,
            "pending",
        )

        self.assertIsNone(
            order.payment_id
        )

        self.assertEqual(
            self.product.stock,
            10,
        )

    # =====================================================
    # VERIFY - SUCCESS
    # =====================================================

    @patch("orders.views.razorpay.Client")
    def test_successful_payment_verification_marks_order_paid(
        self,
        mock_client_class,
    ):
        order = (
            self.create_pending_online_order()
        )

        payment_id = "pay_success_123"

        mock_client = MagicMock()

        mock_client.utility.verify_payment_signature.return_value = (
            None
        )

        mock_client.payment.fetch.return_value = (
            self.valid_fetched_payment(
                order,
                payment_id,
            )
        )

        mock_client_class.return_value = (
            mock_client
        )

        response = self.client.post(
            self.verify_url,
            {
                "razorpay_order_id": (
                    order.razorpay_order_id
                ),
                "razorpay_payment_id": (
                    payment_id
                ),
                "razorpay_signature": (
                    "valid_signature"
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        order.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(
            order.payment_status,
            "paid",
        )

        self.assertEqual(
            order.status,
            "confirmed",
        )

        self.assertEqual(
            order.payment_id,
            payment_id,
        )

        self.assertEqual(
            self.product.stock,
            8,
        )

        mock_client.utility.verify_payment_signature.assert_called_once_with(
            {
                "razorpay_order_id": (
                    order.razorpay_order_id
                ),
                "razorpay_payment_id": (
                    payment_id
                ),
                "razorpay_signature": (
                    "valid_signature"
                ),
            }
        )

        mock_client.payment.fetch.assert_called_once_with(
            payment_id
        )

    # =====================================================
    # VERIFY - RAZORPAY FETCH FAILURE
    # =====================================================

    @patch("orders.views.razorpay.Client")
    def test_payment_fetch_failure_is_rejected(
        self,
        mock_client_class,
    ):
        order = (
            self.create_pending_online_order()
        )

        mock_client = MagicMock()

        mock_client.utility.verify_payment_signature.return_value = (
            None
        )

        mock_client.payment.fetch.side_effect = (
            Exception("Razorpay unavailable")
        )

        mock_client_class.return_value = (
            mock_client
        )

        response = self.client.post(
            self.verify_url,
            {
                "razorpay_order_id": (
                    order.razorpay_order_id
                ),
                "razorpay_payment_id": (
                    "pay_fetch_error_123"
                ),
                "razorpay_signature": (
                    "valid_signature"
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )

        order.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(
            order.payment_status,
            "pending",
        )

        self.assertEqual(
            self.product.stock,
            10,
        )

    # =====================================================
    # VERIFY - WRONG RAZORPAY ORDER ID
    # =====================================================

    @patch("orders.views.razorpay.Client")
    def test_payment_with_mismatched_order_id_is_rejected(
        self,
        mock_client_class,
    ):
        order = (
            self.create_pending_online_order()
        )

        mock_client = MagicMock()

        mock_client.utility.verify_payment_signature.return_value = (
            None
        )

        payment = self.valid_fetched_payment(
            order,
            "pay_wrong_order_123",
        )

        payment["order_id"] = (
            "order_different_999"
        )

        mock_client.payment.fetch.return_value = (
            payment
        )

        mock_client_class.return_value = (
            mock_client
        )

        response = self.client.post(
            self.verify_url,
            {
                "razorpay_order_id": (
                    order.razorpay_order_id
                ),
                "razorpay_payment_id": (
                    "pay_wrong_order_123"
                ),
                "razorpay_signature": (
                    "valid_signature"
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        order.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(
            order.payment_status,
            "pending",
        )

        self.assertEqual(
            self.product.stock,
            10,
        )

    # =====================================================
    # VERIFY - WRONG AMOUNT
    # =====================================================

    @patch("orders.views.razorpay.Client")
    def test_payment_with_wrong_amount_is_rejected(
        self,
        mock_client_class,
    ):
        order = (
            self.create_pending_online_order()
        )

        mock_client = MagicMock()

        mock_client.utility.verify_payment_signature.return_value = (
            None
        )

        payment = self.valid_fetched_payment(
            order,
            "pay_wrong_amount_123",
        )

        # Order total is Rs. 998 = 99800 paise.
        payment["amount"] = 100

        mock_client.payment.fetch.return_value = (
            payment
        )

        mock_client_class.return_value = (
            mock_client
        )

        response = self.client.post(
            self.verify_url,
            {
                "razorpay_order_id": (
                    order.razorpay_order_id
                ),
                "razorpay_payment_id": (
                    "pay_wrong_amount_123"
                ),
                "razorpay_signature": (
                    "valid_signature"
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        order.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(
            order.payment_status,
            "pending",
        )

        self.assertEqual(
            self.product.stock,
            10,
        )

    # =====================================================
    # VERIFY - WRONG CURRENCY
    # =====================================================

    @patch("orders.views.razorpay.Client")
    def test_payment_with_wrong_currency_is_rejected(
        self,
        mock_client_class,
    ):
        order = (
            self.create_pending_online_order()
        )

        mock_client = MagicMock()

        mock_client.utility.verify_payment_signature.return_value = (
            None
        )

        payment = self.valid_fetched_payment(
            order,
            "pay_wrong_currency_123",
        )

        payment["currency"] = "USD"

        mock_client.payment.fetch.return_value = (
            payment
        )

        mock_client_class.return_value = (
            mock_client
        )

        response = self.client.post(
            self.verify_url,
            {
                "razorpay_order_id": (
                    order.razorpay_order_id
                ),
                "razorpay_payment_id": (
                    "pay_wrong_currency_123"
                ),
                "razorpay_signature": (
                    "valid_signature"
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        order.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(
            order.payment_status,
            "pending",
        )

        self.assertEqual(
            self.product.stock,
            10,
        )

    # =====================================================
    # VERIFY - PAYMENT NOT CAPTURED
    # =====================================================

    @patch("orders.views.razorpay.Client")
    def test_uncaptured_payment_is_rejected(
        self,
        mock_client_class,
    ):
        order = (
            self.create_pending_online_order()
        )

        mock_client = MagicMock()

        mock_client.utility.verify_payment_signature.return_value = (
            None
        )

        payment = self.valid_fetched_payment(
            order,
            "pay_uncaptured_123",
        )

        payment["status"] = "authorized"
        payment["captured"] = False

        mock_client.payment.fetch.return_value = (
            payment
        )

        mock_client_class.return_value = (
            mock_client
        )

        response = self.client.post(
            self.verify_url,
            {
                "razorpay_order_id": (
                    order.razorpay_order_id
                ),
                "razorpay_payment_id": (
                    "pay_uncaptured_123"
                ),
                "razorpay_signature": (
                    "valid_signature"
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_409_CONFLICT,
        )

        order.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(
            order.payment_status,
            "pending",
        )

        self.assertEqual(
            self.product.stock,
            10,
        )

    # =====================================================
    # VERIFY - IDEMPOTENCY
    #
    # Same payment must never deduct stock twice.
    # =====================================================

    @patch("orders.views.razorpay.Client")
    def test_duplicate_verification_does_not_reduce_stock_twice(
        self,
        mock_client_class,
    ):
        order = (
            self.create_pending_online_order()
        )

        payment_id = "pay_duplicate_123"

        mock_client = MagicMock()

        mock_client.utility.verify_payment_signature.return_value = (
            None
        )

        mock_client.payment.fetch.return_value = (
            self.valid_fetched_payment(
                order,
                payment_id,
            )
        )

        mock_client_class.return_value = (
            mock_client
        )

        payload = {
            "razorpay_order_id": (
                order.razorpay_order_id
            ),
            "razorpay_payment_id": (
                payment_id
            ),
            "razorpay_signature": (
                "valid_signature"
            ),
        }

        first_response = self.client.post(
            self.verify_url,
            payload,
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            8,
        )

        second_response = self.client.post(
            self.verify_url,
            payload,
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            8,
        )

        # Second request is handled by local idempotency
        # check before another Razorpay call is required.
        self.assertEqual(
            mock_client.payment.fetch.call_count,
            1,
        )

    # =====================================================
    # VERIFY - USER OWNERSHIP
    # =====================================================

    @patch("orders.views.razorpay.Client")
    def test_user_cannot_verify_another_users_order(
        self,
        mock_client_class,
    ):
        other_user = User.objects.create_user(
            username="other@example.com",
            email="other@example.com",
            password="TestPassword123!",
        )

        order = Order.objects.create(
            user=other_user,
            customer_name="Other Customer",
            email="other@example.com",
            phone="9876543211",
            address="456 Other Payment Street",
            city="Chennai",
            postal_code="600001",
            status="pending",
            total_amount=Decimal("998.00"),
            payment_method="online",
            payment_status="pending",
            razorpay_order_id=(
                "order_other_user_123"
            ),
        )

        response = self.client.post(
            self.verify_url,
            {
                "razorpay_order_id": (
                    order.razorpay_order_id
                ),
                "razorpay_payment_id": (
                    "pay_other_123"
                ),
                "razorpay_signature": (
                    "signature"
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        mock_client_class.assert_not_called()

    # =====================================================
    # VERIFY - STOCK CHANGED BEFORE PAYMENT COMPLETES
    # =====================================================

    @patch("orders.views.razorpay.Client")
    def test_payment_verification_detects_stock_change(
        self,
        mock_client_class,
    ):
        order = (
            self.create_pending_online_order()
        )

        # Customer originally needed 2 units,
        # but only 1 remains before verification.
        self.product.stock = 1

        self.product.save(
            update_fields=["stock"]
        )

        payment_id = "pay_stock_123"

        mock_client = MagicMock()

        mock_client.utility.verify_payment_signature.return_value = (
            None
        )

        mock_client.payment.fetch.return_value = (
            self.valid_fetched_payment(
                order,
                payment_id,
            )
        )

        mock_client_class.return_value = (
            mock_client
        )

        response = self.client.post(
            self.verify_url,
            {
                "razorpay_order_id": (
                    order.razorpay_order_id
                ),
                "razorpay_payment_id": (
                    payment_id
                ),
                "razorpay_signature": (
                    "valid_signature"
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_409_CONFLICT,
        )

        self.assertTrue(
            response.data["payment_received"]
        )

        self.assertTrue(
            response.data["requires_refund"]
        )

        order.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(
            order.payment_status,
            "refund_pending",
        )

        self.assertEqual(
            self.product.stock,
            1,
        )
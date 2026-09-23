import { useState } from "react";
import { Link } from "react-router-dom";

import api from "../services/api";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";

import "./CheckoutPage.css";


// =========================================================
// RAZORPAY CHECKOUT SCRIPT
// =========================================================

const loadRazorpayScript = () => {
  return new Promise((resolve) => {
    if (window.Razorpay) {
      resolve(true);
      return;
    }

    const existingScript = document.querySelector(
      'script[src="https://checkout.razorpay.com/v1/checkout.js"]'
    );

    if (existingScript) {
      existingScript.addEventListener(
        "load",
        () => resolve(true),
        { once: true }
      );

      existingScript.addEventListener(
        "error",
        () => resolve(false),
        { once: true }
      );

      return;
    }

    const script = document.createElement("script");

    script.src =
      "https://checkout.razorpay.com/v1/checkout.js";

    script.async = true;

    script.onload = () => {
      resolve(true);
    };

    script.onerror = () => {
      resolve(false);
    };

    document.body.appendChild(script);
  });
};


function CheckoutPage() {
  const {
    cartItems,
    cartTotal,
    clearCart,
  } = useCart();

  const { token } = useAuth();

  const [formData, setFormData] = useState({
    customer_name: "",
    email: "",
    phone: "",
    address: "",
    city: "",
    postal_code: "",
    payment_method: "cod",
  });

  const [submitting, setSubmitting] =
    useState(false);

  const [error, setError] =
    useState("");

  const [orderSuccess, setOrderSuccess] =
    useState(null);


  // =====================================================
  // COD AVAILABLE CITIES
  // =====================================================

  const normalizedCity = formData.city
    .trim()
    .toLowerCase();

  const isCodAvailable =
    normalizedCity === "erode" ||
    normalizedCity === "sathy" ||
    normalizedCity === "sathyamangalam" ||
    normalizedCity === "gobi" ||
    normalizedCity === "gobichettipalayam";


  // =====================================================
  // INPUT CHANGE
  // =====================================================

  const handleChange = (event) => {
    const { name, value } = event.target;

    let cleanedValue = value;

    if (name === "phone") {
      cleanedValue = value
        .replace(/\D/g, "")
        .slice(0, 10);
    }

    if (name === "postal_code") {
      cleanedValue = value
        .replace(/\D/g, "")
        .slice(0, 6);
    }

    setFormData((currentData) => ({
      ...currentData,
      [name]: cleanedValue,
    }));

    setError("");
  };


  // =====================================================
  // FRONTEND VALIDATION
  // =====================================================

  const validateForm = () => {
    const customerName =
      formData.customer_name.trim();

    const email =
      formData.email.trim();

    const phone =
      formData.phone.trim();

    const address =
      formData.address.trim();

    const city =
      formData.city.trim();

    const postalCode =
      formData.postal_code.trim();

    if (customerName.length < 2) {
      return (
        "Please enter a valid customer name."
      );
    }

    if (!email) {
      return (
        "Please enter a valid email address."
      );
    }

    if (!/^[6-9]\d{9}$/.test(phone)) {
      return (
        "Please enter a valid 10-digit " +
        "Indian mobile number."
      );
    }

    if (address.length < 10) {
      return (
        "Please enter a complete " +
        "delivery address."
      );
    }

    if (city.length < 2) {
      return "Please enter a valid city.";
    }

    if (!/^\d{6}$/.test(postalCode)) {
      return (
        "Please enter a valid " +
        "6-digit PIN code."
      );
    }

    if (
      formData.payment_method === "cod" &&
      !isCodAvailable
    ) {
      return (
        "Cash on Delivery is currently " +
        "available only in Erode, " +
        "Sathyamangalam, and " +
        "Gobichettipalayam."
      );
    }

    return "";
  };


  // =====================================================
  // DJANGO / API ERROR MESSAGE
  // =====================================================

  const getApiErrorMessage = (err) => {
    const data = err.response?.data;

    if (!data) {
      return (
        "Unable to connect to the server. " +
        "Please try again."
      );
    }

    if (typeof data.detail === "string") {
      return data.detail;
    }

    const preferredFields = [
      "customer_name",
      "phone",
      "email",
      "address",
      "city",
      "postal_code",
      "payment_method",
      "items",
      "non_field_errors",
    ];

    for (const field of preferredFields) {
      const fieldError = data[field];

      if (
        Array.isArray(fieldError) &&
        fieldError.length > 0
      ) {
        const firstError =
          fieldError[0];

        if (
          typeof firstError === "string"
        ) {
          return firstError;
        }

        if (
          typeof firstError === "object"
        ) {
          const nestedErrors =
            Object.values(
              firstError
            ).flat();

          if (
            nestedErrors.length > 0
          ) {
            return String(
              nestedErrors[0]
            );
          }
        }
      }

      if (
        typeof fieldError === "string"
      ) {
        return fieldError;
      }
    }

    return (
      "Unable to place your order. " +
      "Please check your details and " +
      "try again."
    );
  };


  // =====================================================
  // COMMON CUSTOMER / CART DATA
  // =====================================================

  const buildOrderData = () => ({
    customer_name:
      formData.customer_name.trim(),

    email:
      formData.email.trim(),

    phone:
      formData.phone.trim(),

    address:
      formData.address.trim(),

    city:
      formData.city.trim(),

    postal_code:
      formData.postal_code.trim(),

    items: cartItems.map((item) => ({
      product_id: item.id,
      quantity: item.quantity,
    })),
  });


  // =====================================================
  // RESET AFTER SUCCESS
  // =====================================================

  const completeOrder = (
    successData
  ) => {
    setOrderSuccess(successData);

    clearCart();

    setFormData({
      customer_name: "",
      email: "",
      phone: "",
      address: "",
      city: "",
      postal_code: "",
      payment_method: "cod",
    });
  };


  // =====================================================
  // CASH ON DELIVERY
  // =====================================================

  const placeCodOrder = async () => {
    const orderData = {
      ...buildOrderData(),
      payment_method: "cod",
    };

    const response = await api.post(
      "/orders/",
      orderData,
      {
        headers: {
          Authorization:
            `Token ${token}`,
        },
      }
    );

    completeOrder(
      response.data
    );
  };


  // =====================================================
  // ONLINE PAYMENT - RAZORPAY
  // =====================================================

  const placeOnlineOrder = async () => {
    // ---------------------------------------------------
    // Load official Razorpay Checkout script
    // ---------------------------------------------------

    const scriptLoaded =
      await loadRazorpayScript();

    if (!scriptLoaded) {
      throw new Error(
        "RAZORPAY_SCRIPT_FAILED"
      );
    }

    // ---------------------------------------------------
    // Ask Django to calculate total and create
    // Razorpay + local pending order.
    // ---------------------------------------------------

    const createResponse =
      await api.post(
        "/orders/razorpay/create/",
        buildOrderData(),
        {
          headers: {
            Authorization:
              `Token ${token}`,
          },
        }
      );

    const paymentOrder =
      createResponse.data;

    if (
      !paymentOrder.razorpay_order_id ||
      !paymentOrder.razorpay_key_id ||
      !paymentOrder.amount
    ) {
      throw new Error(
        "INVALID_PAYMENT_ORDER"
      );
    }

    // ---------------------------------------------------
    // Open Razorpay Checkout
    // ---------------------------------------------------

    const options = {
      key:
        paymentOrder.razorpay_key_id,

      amount:
        paymentOrder.amount,

      currency:
        paymentOrder.currency ||
        "INR",

      name:
        "Lovely Mobi Care",

      description:
        `Order #${paymentOrder.order_id}`,

      order_id:
        paymentOrder.razorpay_order_id,

      prefill: {
        name:
          formData.customer_name.trim(),

        email:
          formData.email.trim(),

        contact:
          formData.phone.trim(),
      },

      notes: {
        local_order_id:
          String(
            paymentOrder.order_id
          ),
      },

      handler: async (
        paymentResponse
      ) => {
        try {
          setSubmitting(true);
          setError("");

          // ---------------------------------------------
          // Never mark the order successful from
          // browser data alone.
          //
          // Django verifies the Razorpay signature.
          // ---------------------------------------------

          const verifyResponse =
            await api.post(
              "/orders/razorpay/verify/",
              {
                razorpay_order_id:
                  paymentResponse
                    .razorpay_order_id,

                razorpay_payment_id:
                  paymentResponse
                    .razorpay_payment_id,

                razorpay_signature:
                  paymentResponse
                    .razorpay_signature,
              },
              {
                headers: {
                  Authorization:
                    `Token ${token}`,
                },
              }
            );

          const verified =
            verifyResponse.data;

          completeOrder({
            id:
              verified.order_id,

            status:
              verified.status ||
              "confirmed",

            payment_method:
              "online",

            payment_status:
              verified.payment_status ||
              "paid",

            total_amount:
              verified.total_amount ||
              paymentOrder.total_amount,

            payment_id:
              verified.payment_id,
          });

        } catch (verifyError) {
          console.error(
            "Payment verification error:",
            verifyError
          );

          const responseData =
            verifyError.response?.data;

          if (
            responseData
              ?.payment_received
          ) {
            setError(
              responseData.detail ||
              (
                "Payment was received, but " +
                "your order needs manual " +
                "verification. Please do not " +
                "make another payment."
              )
            );
          } else {
            setError(
              getApiErrorMessage(
                verifyError
              )
            );
          }

        } finally {
          setSubmitting(false);
        }
      },

      modal: {
        ondismiss: () => {
          setSubmitting(false);

          setError(
            "Online payment was not completed. " +
            "Your cart has not been cleared."
          );
        },
      },

      theme: {
        color: "#111827",
      },
    };

    const razorpayCheckout =
      new window.Razorpay(options);

    razorpayCheckout.on(
      "payment.failed",
      (failureResponse) => {
        console.error(
          "Razorpay payment failed:",
          failureResponse
        );

        setSubmitting(false);

        const description =
          failureResponse?.error
            ?.description;

        setError(
          description ||
          (
            "Online payment failed. " +
            "Please try again."
          )
        );
      }
    );

    razorpayCheckout.open();

    // Checkout is now controlling the flow.
    // Stop showing "starting payment".
    setSubmitting(false);
  };


  // =====================================================
  // PLACE ORDER
  // =====================================================

  const handleSubmit = async (
    event
  ) => {
    event.preventDefault();

    setError("");

    if (cartItems.length === 0) {
      setError(
        "Your cart is empty."
      );
      return;
    }

    if (!token) {
      setError(
        "Please login before placing " +
        "your order."
      );
      return;
    }

    const validationError =
      validateForm();

    if (validationError) {
      setError(
        validationError
      );
      return;
    }

    setSubmitting(true);

    try {
      if (
        formData.payment_method ===
        "online"
      ) {
        await placeOnlineOrder();
      } else {
        await placeCodOrder();
      }

    } catch (err) {
      console.error(
        "Checkout error:",
        err
      );

      if (
        err.message ===
        "RAZORPAY_SCRIPT_FAILED"
      ) {
        setError(
          "Unable to load the secure " +
          "payment window. Please check " +
          "your internet connection and " +
          "try again."
        );

      } else if (
        err.message ===
        "INVALID_PAYMENT_ORDER"
      ) {
        setError(
          "Unable to start online payment. " +
          "Please try again."
        );

      } else {
        setError(
          getApiErrorMessage(err)
        );
      }

    } finally {
      if (
        formData.payment_method !==
        "online"
      ) {
        setSubmitting(false);
      }
    }
  };


  // =====================================================
  // SUCCESS PAGE
  // =====================================================

  if (orderSuccess) {
    return (
      <main className="checkout-page">
        <section className="checkout-success-section">
          <div className="checkout-success-card">

            <div className="checkout-success-icon">
              ✓
            </div>

            <span>
              ORDER PLACED
            </span>

            <h1>
              Thank You for Your Order!
            </h1>

            <p>
              Your order has been received
              successfully by Lovely Mobi Care.
            </p>

            <div className="order-number">
              <small>
                Your Order ID
              </small>

              <strong>
                #{orderSuccess.id}
              </strong>
            </div>

            <div className="success-order-details">

              <div>
                <span>
                  Status
                </span>

                <strong>
                  {orderSuccess.status ||
                    "pending"}
                </strong>
              </div>

              <div>
                <span>
                  Payment
                </span>

                <strong>
                  {orderSuccess.payment_method ===
                  "cod"
                    ? "Cash on Delivery"
                    : "Online Payment"}
                </strong>
              </div>

              <div>
                <span>
                  Payment Status
                </span>

                <strong>
                  {orderSuccess.payment_status ||
                    "pending"}
                </strong>
              </div>

              <div>
                <span>
                  Order Total
                </span>

                <strong>
                  ₹
                  {Number(
                    orderSuccess.total_amount
                  ).toLocaleString(
                    "en-IN"
                  )}
                </strong>
              </div>

            </div>

            <p className="checkout-success-note">
              Keep your Order ID safe. You can
              view your order status anytime
              from My Orders.
            </p>

            <div className="checkout-success-actions">

              <Link
                to="/my-orders"
                className="continue-shopping-button"
              >
                Track My Order
              </Link>

              <Link
                to="/products"
                className="continue-shopping-button"
              >
                Continue Shopping
              </Link>

            </div>

          </div>
        </section>
      </main>
    );
  }


  // =====================================================
  // CHECKOUT PAGE
  // =====================================================

  return (
    <main className="checkout-page">

      <section className="checkout-header">
        <span>
          CHECKOUT
        </span>

        <h1>
          Complete Your Order
        </h1>

        <p>
          Enter your contact and delivery
          details to place your order with
          Lovely Mobi Care.
        </p>
      </section>


      <section className="checkout-container">

        {cartItems.length === 0 ? (

          <div className="checkout-empty">

            <div className="checkout-empty-icon">
              🛒
            </div>

            <h2>
              Your cart is empty
            </h2>

            <p>
              Add a product to your cart
              before proceeding to checkout.
            </p>

            <Link
              to="/products"
              className="checkout-products-button"
            >
              Browse Products
            </Link>

          </div>

        ) : (

          <div className="checkout-layout">

            <form
              className="checkout-form"
              onSubmit={handleSubmit}
            >

              <div className="checkout-form-heading">

                <span>
                  CUSTOMER DETAILS
                </span>

                <h2>
                  Contact & Delivery Information
                </h2>

              </div>


              {error && (
                <div className="checkout-error">
                  {error}
                </div>
              )}


              <div className="checkout-form-grid">

                {/* FULL NAME */}

                <div className="checkout-form-group">

                  <label htmlFor="customer_name">
                    Full Name *
                  </label>

                  <input
                    id="customer_name"
                    type="text"
                    name="customer_name"
                    value={
                      formData.customer_name
                    }
                    onChange={handleChange}
                    placeholder="Enter your full name"
                    minLength="2"
                    maxLength="150"
                    autoComplete="name"
                    required
                  />

                </div>


                {/* PHONE */}

                <div className="checkout-form-group">

                  <label htmlFor="phone">
                    Phone Number *
                  </label>

                  <input
                    id="phone"
                    type="tel"
                    name="phone"
                    value={
                      formData.phone
                    }
                    onChange={handleChange}
                    placeholder="10-digit mobile number"
                    inputMode="numeric"
                    autoComplete="tel"
                    maxLength="10"
                    pattern="[6-9][0-9]{9}"
                    title="Enter a valid 10-digit Indian mobile number"
                    required
                  />

                </div>


                {/* EMAIL */}

                <div className="checkout-form-group full-width">

                  <label htmlFor="email">
                    Email Address *
                  </label>

                  <input
                    id="email"
                    type="email"
                    name="email"
                    value={
                      formData.email
                    }
                    onChange={handleChange}
                    placeholder="Enter your email"
                    autoComplete="email"
                    required
                  />

                </div>


                {/* ADDRESS */}

                <div className="checkout-form-group full-width">

                  <label htmlFor="address">
                    Delivery Address *
                  </label>

                  <textarea
                    id="address"
                    name="address"
                    value={
                      formData.address
                    }
                    onChange={handleChange}
                    rows="4"
                    placeholder="House number, street, area..."
                    minLength="10"
                    autoComplete="street-address"
                    required
                  />

                </div>


                {/* CITY */}

                <div className="checkout-form-group">

                  <label htmlFor="city">
                    City *
                  </label>

                  <input
                    id="city"
                    type="text"
                    name="city"
                    value={
                      formData.city
                    }
                    onChange={handleChange}
                    placeholder="Enter your city"
                    autoComplete="address-level2"
                    required
                  />

                </div>


                {/* POSTAL CODE */}

                <div className="checkout-form-group">

                  <label htmlFor="postal_code">
                    Postal Code *
                  </label>

                  <input
                    id="postal_code"
                    type="text"
                    name="postal_code"
                    value={
                      formData.postal_code
                    }
                    onChange={handleChange}
                    placeholder="6-digit PIN code"
                    inputMode="numeric"
                    autoComplete="postal-code"
                    maxLength="6"
                    pattern="[0-9]{6}"
                    title="Enter a valid 6-digit PIN code"
                    required
                  />

                </div>


                {/* =====================================
                    PAYMENT METHOD
                ====================================== */}

                <div className="payment-section">

                  <span className="payment-section-label">
                    PAYMENT METHOD
                  </span>

                  <h3>
                    Choose Payment Method
                  </h3>


                  {/* CASH ON DELIVERY */}

                  <label
                    className={`payment-option ${
                      formData.payment_method ===
                        "cod" &&
                      isCodAvailable
                        ? "payment-option-selected"
                        : !isCodAvailable
                        ? "payment-option-disabled"
                        : ""
                    }`}
                  >

                    <input
                      type="radio"
                      name="payment_method"
                      value="cod"
                      checked={
                        formData.payment_method ===
                        "cod"
                      }
                      onChange={handleChange}
                      disabled={
                        !isCodAvailable
                      }
                    />

                    <div className="payment-option-icon">
                      💵
                    </div>

                    <div className="payment-option-content">

                      <strong>
                        Cash on Delivery
                      </strong>

                      {isCodAvailable ? (
                        <span className="cod-available">
                          ✓ Available in your city
                        </span>
                      ) : (
                        <span className="cod-unavailable">
                          COD is available only in
                          Erode, Sathyamangalam and
                          Gobichettipalayam.
                        </span>
                      )}

                    </div>

                    {isCodAvailable ? (
                      <small className="available-badge">
                        Available
                      </small>
                    ) : (
                      <small className="unavailable-badge">
                        Unavailable
                      </small>
                    )}

                  </label>


                  {/* ONLINE PAYMENT */}

                  <label
                    className={`payment-option ${
                      formData.payment_method ===
                      "online"
                        ? "payment-option-selected"
                        : ""
                    }`}
                  >

                    <input
                      type="radio"
                      name="payment_method"
                      value="online"
                      checked={
                        formData.payment_method ===
                        "online"
                      }
                      onChange={handleChange}
                    />

                    <div className="payment-option-icon">
                      💳
                    </div>

                    <div className="payment-option-content">

                      <strong>
                        Online Payment
                      </strong>

                      <span>
                        Pay securely using UPI,
                        Cards and supported
                        Razorpay payment methods.
                      </span>

                    </div>

                    <small className="available-badge">
                      Available
                    </small>

                  </label>

                </div>

              </div>


              {/* PLACE ORDER / PAY BUTTON */}

              <button
                type="submit"
                className="place-order-button"
                disabled={
                  submitting ||
                  (
                    formData.payment_method ===
                      "cod" &&
                    !isCodAvailable
                  )
                }
              >

                {submitting
                  ? formData.payment_method ===
                    "online"
                    ? "Starting Payment..."
                    : "Placing Order..."
                  : formData.payment_method ===
                    "online"
                  ? `Pay Online — ₹${Number(
                      cartTotal
                    ).toLocaleString(
                      "en-IN"
                    )}`
                  : !isCodAvailable
                  ? "COD Currently Unavailable"
                  : `Place Order — ₹${Number(
                      cartTotal
                    ).toLocaleString(
                      "en-IN"
                    )}`}

              </button>


              <p className="checkout-submit-note">

                {formData.payment_method ===
                "online"
                  ? (
                    "Your payment will be " +
                    "securely processed through " +
                    "Razorpay."
                  )
                  : isCodAvailable
                  ? (
                    "Cash on Delivery is " +
                    "available for your city."
                  )
                  : (
                    "Select Online Payment, or " +
                    "enter Erode, Sathyamangalam, " +
                    "or Gobichettipalayam to use COD."
                  )}

              </p>

            </form>


            {/* =====================================
                ORDER SUMMARY
            ====================================== */}

            <aside className="checkout-summary">

              <div className="checkout-summary-heading">

                <span>
                  YOUR ORDER
                </span>

                <h2>
                  Order Summary
                </h2>

              </div>


              <div className="checkout-items">

                {cartItems.map((item) => (

                  <div
                    className="checkout-item"
                    key={item.id}
                  >

                    <div className="checkout-item-image">

                      {item.image ? (
                        <img
                          src={item.image}
                          alt={item.name}
                        />
                      ) : (
                        <span>
                          📱
                        </span>
                      )}

                    </div>


                    <div className="checkout-item-info">

                      <strong>
                        {item.name}
                      </strong>

                      <small>
                        Qty: {item.quantity}
                      </small>

                      <span>
                        ₹
                        {Number(
                          item.price
                        ).toLocaleString(
                          "en-IN"
                        )}
                      </span>

                    </div>


                    <strong className="checkout-item-total">
                      ₹
                      {(
                        Number(item.price) *
                        item.quantity
                      ).toLocaleString(
                        "en-IN"
                      )}
                    </strong>

                  </div>

                ))}

              </div>


              <div className="checkout-price-row">

                <span>
                  Subtotal
                </span>

                <strong>
                  ₹
                  {Number(
                    cartTotal
                  ).toLocaleString(
                    "en-IN"
                  )}
                </strong>

              </div>


              <div className="checkout-price-row">

                <span>
                  Delivery
                </span>

                <small>
                  To be confirmed
                </small>

              </div>


              <div className="checkout-price-row">

                <span>
                  Payment
                </span>

                <strong>
                  {formData.payment_method ===
                  "online"
                    ? "Online Payment"
                    : isCodAvailable
                    ? "Cash on Delivery"
                    : "COD Unavailable"}
                </strong>

              </div>


              <div className="checkout-total-row">

                <span>
                  Total
                </span>

                <strong>
                  ₹
                  {Number(
                    cartTotal
                  ).toLocaleString(
                    "en-IN"
                  )}
                </strong>

              </div>


              <Link
                to="/cart"
                className="edit-cart-link"
              >
                ← Edit Cart
              </Link>

            </aside>

          </div>

        )}

      </section>

    </main>
  );
}


export default CheckoutPage;
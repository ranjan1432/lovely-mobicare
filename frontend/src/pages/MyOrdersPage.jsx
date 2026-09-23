import {
  useEffect,
  useMemo,
  useState,
} from "react";

import { Link } from "react-router-dom";

import api from "../services/api";
import { useAuth } from "../context/AuthContext";

import "./MyOrdersPage.css";


const STATUS_STEPS = [
  {
    key: "pending",
    label: "Order Placed",
  },
  {
    key: "confirmed",
    label: "Confirmed",
  },
  {
    key: "processing",
    label: "Processing",
  },
  {
    key: "completed",
    label: "Completed",
  },
];


const STATUS_INDEX = {
  pending: 0,
  confirmed: 1,
  processing: 2,
  completed: 3,
};


const FILTERS = [
  {
    key: "all",
    label: "All Orders",
  },
  {
    key: "processing",
    label: "Processing",
  },
  {
    key: "completed",
    label: "Completed",
  },
  {
    key: "cancelled",
    label: "Cancelled",
  },
];


function formatDate(dateString) {
  if (!dateString) {
    return "-";
  }

  return new Date(dateString).toLocaleString(
    "en-IN",
    {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }
  );
}


function formatMoney(value) {
  const amount = Number(value || 0);

  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}


function getStatusLabel(status) {
  const labels = {
    pending: "Order Placed",
    confirmed: "Confirmed",
    processing: "Processing",
    completed: "Completed",
    cancelled: "Cancelled",
  };

  return labels[status] || status;
}


function MyOrdersPage() {
  const {
    token,
    user,
    authLoading,
  } = useAuth();

  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [activeFilter, setActiveFilter] =
    useState("all");


  // =====================================================
  // LOAD LOGGED-IN USER'S ORDERS
  // =====================================================

  useEffect(() => {
    const loadOrders = async () => {
      if (authLoading) {
        return;
      }

      if (!token) {
        setOrders([]);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError("");

        const response = await api.get(
          "/orders/my-orders/",
          {
            headers: {
              Authorization: `Token ${token}`,
            },
          }
        );

        setOrders(
          Array.isArray(response.data)
            ? response.data
            : []
        );
      } catch (err) {
        console.error(
          "My Orders loading error:",
          err
        );

        const message =
          err.response?.data?.detail ||
          "Unable to load your orders. Please try again.";

        setError(message);
        setOrders([]);
      } finally {
        setLoading(false);
      }
    };

    loadOrders();
  }, [token, authLoading]);


  // =====================================================
  // FILTER ORDERS
  // =====================================================

  const filteredOrders = useMemo(() => {
    if (activeFilter === "all") {
      return orders;
    }

    if (activeFilter === "processing") {
      return orders.filter((order) =>
        [
          "pending",
          "confirmed",
          "processing",
        ].includes(order.status)
      );
    }

    return orders.filter(
      (order) =>
        order.status === activeFilter
    );
  }, [orders, activeFilter]);


  // =====================================================
  // FILTER COUNT
  // =====================================================

  const getFilterCount = (filterKey) => {
    if (filterKey === "all") {
      return orders.length;
    }

    if (filterKey === "processing") {
      return orders.filter((order) =>
        [
          "pending",
          "confirmed",
          "processing",
        ].includes(order.status)
      ).length;
    }

    return orders.filter(
      (order) =>
        order.status === filterKey
    ).length;
  };


  // =====================================================
  // LOADING AUTH
  // =====================================================

  if (authLoading) {
    return (
      <div className="my-orders-page">
        <section className="orders-content">
          <div className="orders-loading">
            <div className="loading-spinner" />

            <p>
              Checking your account...
            </p>
          </div>
        </section>
      </div>
    );
  }


  // =====================================================
  // NOT LOGGED IN
  // Backup protection
  // =====================================================

  if (!token) {
    return (
      <div className="my-orders-page">
        <section className="orders-content">
          <div className="orders-empty">
            <div className="empty-icon">
              🔐
            </div>

            <h2>
              Login to view your orders
            </h2>

            <p>
              Sign in to your Lovely Mobi Care
              account to view your purchases and
              track their latest status.
            </p>

            <Link
              to="/login"
              className="orders-primary-button"
            >
              Login to Continue
            </Link>
          </div>
        </section>
      </div>
    );
  }


  return (
    <div className="my-orders-page">

      {/* ===============================================
          HERO
      ================================================ */}

      <section className="orders-hero">
        <div className="orders-hero-inner account-orders-hero">

          <div className="orders-heading">
            <span className="orders-eyebrow">
              YOUR PURCHASES
            </span>

            <h1>
              My Orders
            </h1>

            <p>
              Track and manage all your Lovely
              Mobi Care purchases in one place.
            </p>

            <div className="orders-benefits">

              <div className="benefit-item">
                <div className="benefit-icon">
                  ✓
                </div>

                <div>
                  <strong>
                    Quality Products
                  </strong>

                  <span>
                    Trusted accessories
                  </span>
                </div>
              </div>

              <div className="benefit-item">
                <div className="benefit-icon">
                  ⚡
                </div>

                <div>
                  <strong>
                    Fast Service
                  </strong>

                  <span>
                    Local delivery support
                  </span>
                </div>
              </div>

              <div className="benefit-item">
                <div className="benefit-icon">
                  ◆
                </div>

                <div>
                  <strong>
                    Secure Orders
                  </strong>

                  <span>
                    Account protected
                  </span>
                </div>
              </div>

            </div>
          </div>


          {/* ACCOUNT CARD */}

          <div className="orders-account-card">

            <div className="orders-account-icon">
              👤
            </div>

            <div className="orders-account-content">
              <span>
                SIGNED IN AS
              </span>

              <h2>
                {user?.first_name
                  ? `Hi, ${user.first_name}`
                  : "Your Account"}
              </h2>

              <p>
                {user?.email}
              </p>
            </div>

            <div className="orders-account-stat">
              <strong>
                {orders.length}
              </strong>

              <span>
                {orders.length === 1
                  ? "Order"
                  : "Orders"}
              </span>
            </div>

          </div>

        </div>
      </section>


      {/* ===============================================
          MAIN CONTENT
      ================================================ */}

      <section className="orders-content">

        {/* LOADING */}

        {loading && (
          <div className="orders-loading">
            <div className="loading-spinner" />

            <p>
              Loading your orders...
            </p>
          </div>
        )}


        {/* ERROR */}

        {!loading && error && (
          <div className="orders-empty">

            <div className="empty-icon">
              ⚠️
            </div>

            <h2>
              Unable to load orders
            </h2>

            <p>
              {error}
            </p>

          </div>
        )}


        {/* NO ORDERS */}

        {!loading &&
          !error &&
          orders.length === 0 && (
            <div className="orders-empty">

              <div className="empty-icon">
                📦
              </div>

              <h2>
                No orders yet
              </h2>

              <p>
                You haven't placed any orders
                with this account yet. Browse our
                products and place your first
                order.
              </p>

              <Link
                to="/products"
                className="orders-primary-button"
              >
                Browse Products
              </Link>

            </div>
          )}


        {/* ORDERS */}

        {!loading &&
          !error &&
          orders.length > 0 && (
            <>

              {/* HEADER */}

              <div className="orders-list-header">

                <div>
                  <span className="toolbar-label">
                    ORDER HISTORY
                  </span>

                  <h2>
                    Your Orders
                  </h2>

                  <p>
                    Latest purchases from your
                    account.
                  </p>
                </div>

                <div className="orders-count">
                  <strong>
                    {orders.length}
                  </strong>

                  <span>
                    Total Orders
                  </span>
                </div>

              </div>


              {/* FILTERS */}

              <div className="orders-filters">

                {FILTERS.map((filter) => (
                  <button
                    key={filter.key}
                    type="button"
                    className={
                      activeFilter === filter.key
                        ? "order-filter active"
                        : "order-filter"
                    }
                    onClick={() =>
                      setActiveFilter(
                        filter.key
                      )
                    }
                  >
                    {filter.label}

                    <span>
                      {getFilterCount(
                        filter.key
                      )}
                    </span>
                  </button>
                ))}

              </div>


              {/* NO RESULT FOR FILTER */}

              {filteredOrders.length === 0 && (
                <div className="filter-empty">
                  <div>
                    📦
                  </div>

                  <h3>
                    No orders found
                  </h3>

                  <p>
                    You don't have any orders in
                    this category.
                  </p>
                </div>
              )}


              {/* ORDER CARDS */}

              <div className="orders-list">

                {filteredOrders.map((order) => {

                  const currentStep =
                    order.status !==
                    "cancelled"
                      ? STATUS_INDEX[
                          order.status
                        ] ?? 0
                      : -1;

                  return (
                    <article
                      className="order-card"
                      key={order.id}
                    >

                      {/* CARD TOP */}

                      <div className="order-card-top">

                        <div>
                          <div className="order-title-row">

                            <h3>
                              Order #{order.id}
                            </h3>

                            <span
                              className={
                                `status-badge status-${order.status}`
                              }
                            >
                              {getStatusLabel(
                                order.status
                              )}
                            </span>

                          </div>

                          <p>
                            Placed on{" "}
                            {formatDate(
                              order.created_at
                            )}
                          </p>
                        </div>


                        <div className="order-total-mobile">
                          <span>
                            Order Total
                          </span>

                          <strong>
                            {formatMoney(
                              order.total_amount
                            )}
                          </strong>
                        </div>

                      </div>


                      {/* CARD BODY */}

                      <div className="order-card-body">

                        {/* PRODUCTS */}

                        <div className="order-products">

                          <span className="section-label">
                            ITEMS
                          </span>

                          {order.items?.length >
                          0 ? (
                            order.items.map(
                              (item) => (
                                <div
                                  className="order-product"
                                  key={item.id}
                                >
                                  <div className="product-placeholder">
                                    📱
                                  </div>

                                  <div className="product-information">

                                    <h4>
                                      {
                                        item.product_name
                                      }
                                    </h4>

                                    <p>
                                      Quantity:{" "}
                                      {
                                        item.quantity
                                      }
                                    </p>

                                    <strong>
                                      {formatMoney(
                                        item.price
                                      )}
                                    </strong>

                                  </div>
                                </div>
                              )
                            )
                          ) : (
                            <p className="no-order-items">
                              Product details
                              unavailable.
                            </p>
                          )}

                        </div>


                        {/* PROGRESS */}

                        <div className="order-progress-section">

                          <span className="section-label">
                            ORDER STATUS
                          </span>


                          {order.status ===
                          "cancelled" ? (

                            <div className="cancelled-panel">

                              <div className="cancelled-icon">
                                ×
                              </div>

                              <div>
                                <strong>
                                  Order Cancelled
                                </strong>

                                <p>
                                  This order has
                                  been cancelled.
                                  Contact us if
                                  you need help.
                                </p>
                              </div>

                            </div>

                          ) : (

                            <div className="progress-tracker">

                              {STATUS_STEPS.map(
                                (
                                  step,
                                  index
                                ) => {

                                  const completed =
                                    index <=
                                    currentStep;

                                  const active =
                                    index ===
                                    currentStep;

                                  return (
                                    <div
                                      className={
                                        `progress-step ${
                                          completed
                                            ? "completed"
                                            : ""
                                        } ${
                                          active
                                            ? "active"
                                            : ""
                                        }`
                                      }
                                      key={
                                        step.key
                                      }
                                    >

                                      <div className="step-row">

                                        <div className="step-circle">
                                          {completed
                                            ? "✓"
                                            : index +
                                              1}
                                        </div>

                                        {index <
                                          STATUS_STEPS.length -
                                            1 && (
                                          <div className="step-line" />
                                        )}

                                      </div>


                                      <div className="step-text">

                                        <strong>
                                          {
                                            step.label
                                          }
                                        </strong>

                                        {active && (
                                          <span>
                                            Current
                                            status
                                          </span>
                                        )}

                                      </div>

                                    </div>
                                  );
                                }
                              )}

                            </div>
                          )}

                        </div>


                        {/* SUMMARY */}

                        <div className="order-summary">

                          <span className="section-label">
                            SUMMARY
                          </span>


                          <div className="summary-row">

                            <span>
                              Customer
                            </span>

                            <strong>
                              {
                                order.customer_name
                              }
                            </strong>

                          </div>


                          <div className="summary-row">

                            <span>
                              Payment
                            </span>

                            <strong>
                              {order.payment_method ===
                              "cod"
                                ? "Cash on Delivery"
                                : "Online Payment"}
                            </strong>

                          </div>


                          <div className="summary-row">

                            <span>
                              Payment Status
                            </span>

                            <strong className="capitalize">
                              {
                                order.payment_status
                              }
                            </strong>

                          </div>


                          <div className="summary-divider" />


                          <div className="summary-total">

                            <span>
                              Total Amount
                            </span>

                            <strong>
                              {formatMoney(
                                order.total_amount
                              )}
                            </strong>

                          </div>


                          <Link
                            to="/contact"
                            className="support-button"
                          >
                            Contact Support
                          </Link>

                        </div>

                      </div>


                      {/* LAST UPDATE */}

                      <div className="order-update">

                        <span>
                          ●
                        </span>

                        <span>
                          Last updated:{" "}

                          <strong>
                            {formatDate(
                              order.updated_at
                            )}
                          </strong>
                        </span>

                      </div>

                    </article>
                  );
                })}

              </div>
            </>
          )}

      </section>
    </div>
  );
}


export default MyOrdersPage;
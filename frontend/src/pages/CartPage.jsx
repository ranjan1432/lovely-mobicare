import { Link } from "react-router-dom";
import { useCart } from "../context/CartContext";
import "./CartPage.css";

function CartPage() {
  const {
    cartItems,
    increaseQuantity,
    decreaseQuantity,
    removeFromCart,
    clearCart,
    cartTotal,
  } = useCart();

  return (
    <main className="cart-page">
      <section className="cart-header">
        <span>YOUR CART</span>
        <h1>Shopping Cart</h1>
        <p>Review your selected products before checkout.</p>
      </section>

      <section className="cart-container">
        {cartItems.length === 0 ? (
          <div className="empty-cart">
            <div className="empty-cart-icon">🛒</div>
            <h2>Your cart is empty</h2>
            <p>Add some products to your cart to continue shopping.</p>

            <Link to="/products" className="continue-shopping-button">
              Browse Products
            </Link>
          </div>
        ) : (
          <>
            <div className="cart-layout">
              <div className="cart-items">
                {cartItems.map((item) => (
                  <article className="cart-item" key={item.id}>
                    <div className="cart-item-image-wrapper">
                      {item.image ? (
                        <img
                          src={item.image}
                          alt={item.name}
                          className="cart-item-image"
                        />
                      ) : (
                        <div className="cart-image-placeholder">
                          📱
                        </div>
                      )}
                    </div>

                    <div className="cart-item-details">
                      <span className="cart-item-category">
                        {item.category_name}
                      </span>

                      <h2>{item.name}</h2>

                      <p className="cart-item-price">
                        ₹{Number(item.price).toLocaleString("en-IN")}
                      </p>

                      <div className="quantity-controls">
                        <button
                          onClick={() => decreaseQuantity(item.id)}
                          aria-label={`Decrease ${item.name} quantity`}
                        >
                          −
                        </button>

                        <span>{item.quantity}</span>

                        <button
                          onClick={() => increaseQuantity(item.id)}
                          disabled={item.quantity >= item.stock}
                          aria-label={`Increase ${item.name} quantity`}
                        >
                          +
                        </button>
                      </div>

                      <small className="cart-stock">
                        {item.stock} available
                      </small>
                    </div>

                    <div className="cart-item-right">
                      <strong>
                        ₹
                        {(
                          Number(item.price) * item.quantity
                        ).toLocaleString("en-IN")}
                      </strong>

                      <button
                        className="remove-button"
                        onClick={() => removeFromCart(item.id)}
                      >
                        Remove
                      </button>
                    </div>
                  </article>
                ))}
              </div>

              <aside className="cart-summary">
                <h2>Order Summary</h2>

                <div className="summary-row">
                  <span>Subtotal</span>
                  <span>
                    ₹{cartTotal.toLocaleString("en-IN")}
                  </span>
                </div>

                <div className="summary-row">
                  <span>Delivery</span>
                  <span>Calculated at checkout</span>
                </div>

                <div className="summary-divider"></div>

                <div className="summary-total">
                  <span>Total</span>
                  <strong>
                    ₹{cartTotal.toLocaleString("en-IN")}
                  </strong>
                </div>

                <Link
                  to="/checkout"
                  className="checkout-button"
                >
                  Proceed to Checkout
                </Link>

                <button
                  className="clear-cart-button"
                  onClick={clearCart}
                >
                  Clear Cart
                </button>
              </aside>
            </div>
          </>
        )}
      </section>
    </main>
  );
}

export default CartPage;
import { useEffect, useMemo, useState } from "react";
import api from "../services/api";
import { useCart } from "../context/CartContext";
import "./ProductsPage.css";

const categories = [
  "All",
  "Chargers",
  "Cables",
  "Ear Buds",
  "Power Banks",
  "Mobile Accessories",
  "Smart Watches",
  "Wired Headphones",
  "Neckbands",
];

function ProductsPage() {
  const { addToCart } = useCart();

  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [cartMessage, setCartMessage] = useState("");

  const [activeCategory, setActiveCategory] = useState("All");
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await api.get("/products/");
        setProducts(response.data);
      } catch (err) {
        console.error("Product API error:", err);
        setError(
          "Unable to load products. Please try again."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  const filteredProducts = useMemo(() => {
    const search = searchTerm.trim().toLowerCase();

    return products.filter((product) => {
      const categoryMatch =
        activeCategory === "All" ||
        product.category_name === activeCategory;

      const searchMatch =
        !search ||
        product.name?.toLowerCase().includes(search) ||
        product.description?.toLowerCase().includes(search) ||
        product.category_name?.toLowerCase().includes(search);

      return categoryMatch && searchMatch;
    });
  }, [products, activeCategory, searchTerm]);

  const featuredProducts = useMemo(
    () => products.filter((product) => product.is_featured),
    [products]
  );

  const handleAddToCart = (product) => {
    addToCart(product);

    setCartMessage(
      `${product.name} has been added to your cart!`
    );

    setTimeout(() => {
      setCartMessage("");
    }, 2000);
  };

  const renderProductCard = (product) => (
    <article className="product-card" key={product.id}>
      <div className="product-image-wrapper">
        {product.is_featured && (
          <span className="featured-badge">
            Featured
          </span>
        )}

        {product.image ? (
          <img
            src={product.image}
            alt={product.name}
            className="product-image"
          />
        ) : (
          <div className="product-image-placeholder">
            <span>🎧</span>
            <p>Product image coming soon</p>
          </div>
        )}
      </div>

      <div className="product-info">
        <span className="product-category">
          {product.category_name || "Accessories"}
        </span>

        <h2>{product.name}</h2>

        {product.description && (
          <p className="product-description">
            {product.description}
          </p>
        )}

        <div className="product-bottom">
          <div className="product-price-area">
            <span className="product-price">
              ₹
              {Number(product.price).toLocaleString(
                "en-IN"
              )}
            </span>

            <small
              className={
                product.stock > 0
                  ? "stock available"
                  : "stock unavailable"
              }
            >
              {product.stock > 0
                ? `${product.stock} in stock`
                : "Out of stock"}
            </small>
          </div>

          <button
            type="button"
            className="add-cart-button"
            onClick={() => handleAddToCart(product)}
            disabled={product.stock <= 0}
          >
            {product.stock > 0
              ? "Add to Cart"
              : "Unavailable"}
          </button>
        </div>
      </div>
    </article>
  );

  return (
    <main className="products-page">
      {cartMessage && (
        <div className="cart-success-message">
          ✓ {cartMessage}
        </div>
      )}

      <section className="products-hero">
        <div className="products-hero-content">
          <span className="products-eyebrow">
            LOVELY MOBI CARE
          </span>

          <h1>
            Accessories That Match
            <br />
            Your Everyday Life
          </h1>

          <p>
            Explore chargers, earbuds, smart watches,
            power banks and more from trusted brands.
          </p>

          <a
            href="#shop-products"
            className="products-shop-button"
          >
            Shop Products
            <span>→</span>
          </a>
        </div>

        <div
          className="products-hero-visual"
          aria-hidden="true"
        >
          <div className="hero-circle hero-circle-one" />
          <div className="hero-circle hero-circle-two" />

          <div className="hero-product-icon">
            🎧
          </div>
        </div>
      </section>

      <section className="category-section">
        <div className="section-heading">
          <div>
            <span>EXPLORE COLLECTION</span>
            <h2>Shop by Categories</h2>
          </div>

          <p>
            Everything your mobile needs, all in one
            place.
          </p>
        </div>

        <div className="category-scroll">
          {categories.map((category) => (
            <button
              type="button"
              key={category}
              className={
                activeCategory === category
                  ? "category-button active"
                  : "category-button"
              }
              onClick={() =>
                setActiveCategory(category)
              }
            >
              <span className="category-icon">
                {category === "All" && "✦"}
                {category === "Chargers" && "⚡"}
                {category === "Cables" && "🔌"}
                {category === "Ear Buds" && "🎧"}
                {category === "Power Banks" && "🔋"}
                {category === "Mobile Accessories" &&
                  "📱"}
                {category === "Smart Watches" && "⌚"}
                {category === "Wired Headphones" &&
                  "🎵"}
                {category === "Neckbands" && "🎶"}
              </span>

              <span>{category}</span>
            </button>
          ))}
        </div>
      </section>

      {featuredProducts.length > 0 && (
        <section className="featured-products-section">
          <div className="section-heading">
            <div>
              <span>POPULAR PICKS</span>
              <h2>Featured Products</h2>
            </div>

            <p>
              Hand-picked products available at Lovely
              Mobi Care.
            </p>
          </div>

          <div className="products-grid">
            {featuredProducts
              .slice(0, 4)
              .map(renderProductCard)}
          </div>
        </section>
      )}

      <section
        className="products-container"
        id="shop-products"
      >
        <div className="products-toolbar">
          <div className="products-title-area">
            <span>OUR COLLECTION</span>

            <h2>
              {activeCategory === "All"
                ? "All Products"
                : activeCategory}
            </h2>
          </div>

          <div className="product-search">
            <span>⌕</span>

            <input
              type="search"
              placeholder="Search products..."
              value={searchTerm}
              onChange={(event) =>
                setSearchTerm(event.target.value)
              }
            />
          </div>
        </div>

        {loading && (
          <div className="products-message">
            Loading products...
          </div>
        )}

        {!loading && error && (
          <div className="products-message error-message">
            {error}
          </div>
        )}

        {!loading &&
          !error &&
          products.length === 0 && (
            <div className="products-empty-state">
              <div className="empty-state-icon">
                🛍️
              </div>

              <h3>Products Coming Soon</h3>

              <p>
                Our latest mobile accessories collection
                will be available here soon.
              </p>
            </div>
          )}

        {!loading &&
          !error &&
          products.length > 0 &&
          filteredProducts.length === 0 && (
            <div className="products-empty-state">
              <div className="empty-state-icon">
                🔍
              </div>

              <h3>No Products Found</h3>

              <p>
                Try another category or search term.
              </p>
            </div>
          )}

        {!loading &&
          !error &&
          filteredProducts.length > 0 && (
            <div className="products-grid">
              {filteredProducts.map(renderProductCard)}
            </div>
          )}
      </section>

      <section className="products-benefits">
        <div>
          <span>✓</span>
          <strong>Quality Products</strong>
          <small>Trusted accessories</small>
        </div>

        <div>
          <span>⚡</span>
          <strong>Latest Collection</strong>
          <small>Modern mobile essentials</small>
        </div>

        <div>
          <span>₹</span>
          <strong>Best Value</strong>
          <small>Competitive pricing</small>
        </div>

        <div>
          <span>♥</span>
          <strong>Customer Support</strong>
          <small>We're here to help</small>
        </div>
      </section>
    </main>
  );
}

export default ProductsPage;
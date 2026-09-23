import "./Brands.css";

function Brands() {
  const brands = [
    "Apple",
    "Samsung",
    "OnePlus",
    "Xiaomi",
    "Redmi",
    "Realme",
    "OPPO",
    "vivo",
  ];

  return (
    <section className="brands-section">
      <div className="brands-container">
        <div className="brands-heading">
          <span>TRUSTED MOBILE BRANDS</span>

          <h2>Brands We Work With</h2>

          <p>
            We provide mobile sales, accessories, and professional
            repair support for popular smartphone brands.
          </p>
        </div>

        <div className="brands-grid">
          {brands.map((brand) => (
            <div className="brand-card" key={brand}>
              <span>{brand}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default Brands;
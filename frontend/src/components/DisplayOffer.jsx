import { Link } from "react-router-dom";
import "./DisplayOffer.css";

function DisplayOffer() {
  return (
    <section className="display-offer-section">
      <div className="display-offer-container">
        <div className="display-offer-content">
          <span className="display-offer-label">
            SPECIAL REPAIR OFFER
          </span>

          <h2>
            Mobile Display Replacement
            <span> Starting at ₹699</span>
          </h2>

          <p>
            Cracked or damaged mobile display? Get professional
            display replacement service at Lovely Mobi Care with
            quality parts and expert care.
          </p>

          <div className="display-offer-features">
            <div>
              <span>✓</span>
              Quality Parts
            </div>

            <div>
              <span>✓</span>
              Expert Service
            </div>

            <div>
              <span>✓</span>
              Affordable Price
            </div>
          </div>

          <Link
            to="/services#service-enquiry"
            className="display-offer-button"
          >
            Book Display Service
          </Link>
        </div>

        <div className="display-offer-price-card">
          <span>DISPLAY REPLACEMENT</span>

          <small>Starting from</small>

          <strong>
            <sup>₹</sup>699
          </strong>

          <p>
            Final price may vary depending on your mobile
            brand, model, and required replacement part.
          </p>

          <div className="display-offer-badge">
            Professional Mobile Care
          </div>
        </div>
      </div>
    </section>
  );
}

export default DisplayOffer;
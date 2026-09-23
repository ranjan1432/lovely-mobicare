import { Link } from "react-router-dom";
import logo from "../assets/lovely-mobi-care-logo.jpeg";
import "./Hero.css";

function Hero() {
  return (
    <section className="hero">
      <div className="hero-container">

        <div className="hero-content">
          <span className="hero-badge">
            📱 Mobile Sales • Accessories • Service
          </span>

          <h1>
            Your Trusted Mobile
            <span>Sales & Service Center</span>
          </h1>

          <p>
            Shop mobile phones and accessories, or get professional repair
            service for your device — all in one place.
          </p>

          <div className="hero-actions">
            <Link to="/products" className="hero-btn primary-btn">
              Shop Products
            </Link>

            <Link to="/services" className="hero-btn secondary-btn">
              Book a Service
            </Link>
          </div>

          <div className="hero-features">
            <span>✓ Quality Products</span>
            <span>✓ Expert Service</span>
            <span>✓ Trusted Support</span>
          </div>
        </div>

        <div className="hero-visual">
          <div className="phone-card">

            <div className="phone">
              <div className="phone-speaker"></div>

              <div className="phone-screen">

                <img
                  src={logo}
                  alt="Lovely Mobi Care"
                  className="hero-phone-logo"
                />

                <strong>Lovely Mobi Care</strong>
                <small>Sales & Service</small>

              </div>

              <div className="phone-home"></div>
            </div>

            <div className="service-card service-card-top">
              <span>⚡</span>

              <div>
                <strong>Quick Service</strong>
                <small>Professional repairs</small>
              </div>
            </div>

            <div className="service-card service-card-bottom">
              <span>🛡️</span>

              <div>
                <strong>Trusted Care</strong>
                <small>Quality you can trust</small>
              </div>
            </div>

          </div>
        </div>

      </div>
    </section>
  );
}

export default Hero;
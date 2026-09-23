import { useEffect, useState } from "react";
import api from "../services/api";
import "./ServicesPage.css";

function ServicesPage() {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [formData, setFormData] = useState({
    customer_name: "",
    phone: "",
    email: "",
    device_brand: "",
    device_model: "",
    issue: "",
  });

  const [submitting, setSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [formError, setFormError] = useState("");

  useEffect(() => {
    const fetchServices = async () => {
      try {
        const response = await api.get("/services/");
        setServices(response.data);
      } catch (err) {
        console.error("Service API error:", err);
        setError("Unable to load services. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchServices();
  }, []);

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((currentData) => ({
      ...currentData,
      [name]: value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setSubmitting(true);
    setSuccessMessage("");
    setFormError("");

    try {
      await api.post("/services/enquiries/", formData);

      setSuccessMessage(
        "Your service enquiry has been submitted successfully!"
      );

      setFormData({
        customer_name: "",
        phone: "",
        email: "",
        device_brand: "",
        device_model: "",
        issue: "",
      });
    } catch (err) {
      console.error("Service enquiry error:", err);

      setFormError(
        "Unable to submit your enquiry. Please check the details and try again."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="services-page">
      <section className="services-header">
        <span>OUR SERVICES</span>

        <h1>Professional Mobile Repair Services</h1>

        <p>
          Get reliable mobile repair and maintenance services from
          Lovely Mobi Care.
        </p>
      </section>

      <section className="services-container">
        <div className="services-section-title">
          <span>WHAT WE REPAIR</span>

          <h2>Choose a Service</h2>

          <p>
            Quality mobile repair services with professional care.
          </p>
        </div>

        {loading && (
          <div className="services-message">
            Loading services...
          </div>
        )}

        {!loading && error && (
          <div className="services-message services-error">
            {error}
          </div>
        )}

        {!loading && !error && services.length === 0 && (
          <div className="services-message">
            No services available right now.
          </div>
        )}

        {!loading && !error && services.length > 0 && (
          <div className="services-grid">
            {services.map((service) => (
              <article
                className="service-card"
                key={service.id}
              >
                <div className="service-icon">🔧</div>

                <h3>{service.name}</h3>

                <p>{service.description}</p>

                <div className="service-price">
                  <small>Starting from</small>

                  <strong>
                    ₹
                    {Number(
                      service.starting_price
                    ).toLocaleString("en-IN")}
                  </strong>
                </div>

                <a
                  href="#service-enquiry"
                  className="service-enquiry-button"
                >
                  Enquire Now
                </a>
              </article>
            ))}
          </div>
        )}

        <section
          className="service-enquiry-section"
          id="service-enquiry"
        >
          <div className="service-enquiry-heading">
            <span>SERVICE ENQUIRY</span>

            <h2>Need Help With Your Mobile?</h2>

            <p>
              Tell us about your device and the issue.
              Our team will help you with the right service.
            </p>
          </div>

          <form
            className="service-enquiry-form"
            onSubmit={handleSubmit}
          >
            {successMessage && (
              <div className="enquiry-success">
                ✓ {successMessage}
              </div>
            )}

            {formError && (
              <div className="enquiry-error">
                {formError}
              </div>
            )}

            <div className="enquiry-form-grid">
              <div className="form-group">
                <label htmlFor="customer_name">
                  Customer Name *
                </label>

                <input
                  id="customer_name"
                  type="text"
                  name="customer_name"
                  value={formData.customer_name}
                  onChange={handleChange}
                  placeholder="Enter your name"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="phone">
                  Phone Number *
                </label>

                <input
                  id="phone"
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  placeholder="Enter your phone number"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="email">
                  Email *
                </label>

                <input
                  id="email"
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="Enter your email"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="device_brand">
                  Device Brand *
                </label>

                <input
                  id="device_brand"
                  type="text"
                  name="device_brand"
                  value={formData.device_brand}
                  onChange={handleChange}
                  placeholder="Example: Samsung"
                  required
                />
              </div>

              <div className="form-group full-width">
                <label htmlFor="device_model">
                  Device Model *
                </label>

                <input
                  id="device_model"
                  type="text"
                  name="device_model"
                  value={formData.device_model}
                  onChange={handleChange}
                  placeholder="Example: Galaxy S25 Ultra"
                  required
                />
              </div>

              <div className="form-group full-width">
                <label htmlFor="issue">
                  Device Issue *
                </label>

                <textarea
                  id="issue"
                  name="issue"
                  value={formData.issue}
                  onChange={handleChange}
                  placeholder="Describe the problem with your mobile..."
                  rows="5"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              className="submit-enquiry-button"
              disabled={submitting}
            >
              {submitting
                ? "Submitting..."
                : "Submit Service Enquiry"}
            </button>
          </form>
        </section>
      </section>
    </main>
  );
}

export default ServicesPage;
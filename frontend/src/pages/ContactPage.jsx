import { useState } from "react";
import api from "../services/api";
import "./ContactPage.css";

function ContactPage() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    subject: "",
    message: "",
  });

  const [submitting, setSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [formError, setFormError] = useState("");

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
      // Save enquiry in Django / MySQL
      await api.post("/contact/", formData);

      const whatsappNumber = "916379196872";

      const whatsappMessage = `
Hello Lovely Mobi Care,

I would like to make an enquiry.

Name: ${formData.name}
Phone: ${formData.phone}
Email: ${formData.email}
Subject: ${formData.subject}

Message:
${formData.message}
      `.trim();

      const whatsappUrl = `https://wa.me/${whatsappNumber}?text=${encodeURIComponent(
        whatsappMessage
      )}`;

      setSuccessMessage(
        "Enquiry saved successfully. Opening WhatsApp..."
      );

      window.open(whatsappUrl, "_blank");

      setFormData({
        name: "",
        email: "",
        phone: "",
        subject: "",
        message: "",
      });
    } catch (error) {
      console.error("Contact enquiry error:", error);

      setFormError(
        "Unable to submit your enquiry. Please try again."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="contact-page">
      <section className="contact-header">
        <span>CONTACT US</span>

        <h1>We're Here to Help</h1>

        <p>
          Need help with mobile sales, accessories, repairs,
          or service enquiries? Get in touch with Lovely Mobi Care.
        </p>
      </section>

      <section className="contact-container">
        <div className="contact-layout">
          <div className="contact-info">
            <span className="contact-label">
              LOVELY MOBI CARE
            </span>

            <h2>Get in Touch</h2>

            <p className="contact-description">
              Lovely Mobi Care provides freelance mobile sales,
              accessories, and mobile repair support. Contact us
              directly for enquiries and service assistance.
            </p>

            <div className="contact-info-list">
              <div className="contact-info-card">
                <div className="contact-icon">📱</div>

                <div>
                  <small>Service Type</small>
                  <strong>Freelance Mobile Service</strong>
                  <p>
                    Mobile sales, accessories and repair assistance.
                  </p>
                </div>
              </div>

              <div className="contact-info-card">
                <div className="contact-icon">💬</div>

                <div>
                  <small>Call / WhatsApp</small>

                  <strong>
                    <a href="tel:+916379196872">
                      +91 63791 96872
                    </a>
                  </strong>

                  <p>
                    Contact us directly for quick assistance.
                  </p>
                </div>
              </div>

              <div className="contact-info-card">
                <div className="contact-icon">✉️</div>

                <div>
                  <small>Email Us</small>

                  <strong>
                    <a href="mailto:lovelymobicare@gmail.com">
                      lovelymobicare@gmail.com
                    </a>
                  </strong>

                  <p>
                    Send us your questions or service enquiries.
                  </p>
                </div>
              </div>

              <div className="contact-info-card">
                <div className="contact-icon">📍</div>

                <div>
                  <small>Service Location</small>

                  <strong>View Our Location</strong>

                  <p>
                    Check our service location using Google Maps.
                  </p>

                  <a
                    href="https://maps.app.goo.gl/ZLvdYkQufy9KX9Yv6"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="location-button"
                  >
                    Open Google Maps
                  </a>
                </div>
              </div>
            </div>
          </div>

          <form
            className="contact-form"
            onSubmit={handleSubmit}
          >
            <div className="contact-form-heading">
              <h2>Send Us a Message</h2>

              <p>
                Fill in your details and continue the conversation
                with us on WhatsApp.
              </p>
            </div>

            {successMessage && (
              <div className="contact-success">
                ✓ {successMessage}
              </div>
            )}

            {formError && (
              <div className="contact-error">
                {formError}
              </div>
            )}

            <div className="contact-form-grid">
              <div className="contact-form-group">
                <label htmlFor="name">
                  Name *
                </label>

                <input
                  id="name"
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="Enter your name"
                  required
                />
              </div>

              <div className="contact-form-group">
                <label htmlFor="phone">
                  Phone *
                </label>

                <input
                  id="phone"
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  placeholder="Enter phone number"
                  required
                />
              </div>

              <div className="contact-form-group full-width">
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

              <div className="contact-form-group full-width">
                <label htmlFor="subject">
                  Subject *
                </label>

                <input
                  id="subject"
                  type="text"
                  name="subject"
                  value={formData.subject}
                  onChange={handleChange}
                  placeholder="How can we help?"
                  required
                />
              </div>

              <div className="contact-form-group full-width">
                <label htmlFor="message">
                  Message *
                </label>

                <textarea
                  id="message"
                  name="message"
                  value={formData.message}
                  onChange={handleChange}
                  rows="6"
                  placeholder="Write your message..."
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              className="contact-submit-button"
              disabled={submitting}
            >
              {submitting
                ? "Opening WhatsApp..."
                : "Send via WhatsApp"}
            </button>
          </form>
        </div>
      </section>
    </main>
  );
}

export default ContactPage;
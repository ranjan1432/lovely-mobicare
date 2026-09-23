import { useEffect, useState } from "react";

import api from "../services/api";

import "./Reviews.css";


function Reviews() {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [formData, setFormData] = useState({
    customer_name: "",
    rating: 5,
    comment: "",
  });

  const [submitting, setSubmitting] = useState(false);

  const [successMessage, setSuccessMessage] =
    useState("");

  const [formError, setFormError] = useState("");


  // =====================================================
  // LOAD APPROVED REVIEWS
  // =====================================================

  useEffect(() => {
    const fetchReviews = async () => {
      try {
        const response = await api.get(
          "/reviews/"
        );

        setReviews(response.data);
      } catch (err) {
        console.error(
          "Reviews API error:",
          err
        );

        setError(
          "Unable to load customer reviews."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchReviews();
  }, []);


  // =====================================================
  // FORM INPUT CHANGE
  // =====================================================

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((currentData) => ({
      ...currentData,
      [name]: value,
    }));

    setFormError("");
    setSuccessMessage("");
  };


  // =====================================================
  // RATING CHANGE
  // =====================================================

  const handleRating = (rating) => {
    setFormData((currentData) => ({
      ...currentData,
      rating,
    }));

    setFormError("");
    setSuccessMessage("");
  };


  // =====================================================
  // DJANGO API ERROR MESSAGE
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

    const fields = [
      "customer_name",
      "rating",
      "comment",
      "non_field_errors",
    ];

    for (const field of fields) {
      const fieldError = data[field];

      if (
        Array.isArray(fieldError) &&
        fieldError.length > 0
      ) {
        return String(fieldError[0]);
      }

      if (typeof fieldError === "string") {
        return fieldError;
      }
    }

    return (
      "Unable to submit your review. " +
      "Please try again."
    );
  };


  // =====================================================
  // SUBMIT REVIEW
  // =====================================================

  const handleSubmit = async (event) => {
    event.preventDefault();

    setSuccessMessage("");
    setFormError("");

    const customerName =
      formData.customer_name.trim();

    const comment =
      formData.comment.trim();


    // CUSTOMER NAME VALIDATION

    if (customerName.length < 2) {
      setFormError(
        "Please enter a valid customer name."
      );

      return;
    }


    // RATING VALIDATION

    if (
      formData.rating < 1 ||
      formData.rating > 5
    ) {
      setFormError(
        "Please select a valid rating."
      );

      return;
    }


    // REVIEW COMMENT VALIDATION

    if (comment.length < 5) {
      setFormError(
        "Please write a more detailed review."
      );

      return;
    }


    if (comment.length > 2000) {
      setFormError(
        "Review is too long."
      );

      return;
    }


    setSubmitting(true);


    const reviewData = {
      customer_name: customerName,
      rating: formData.rating,
      comment,
    };


    try {
      await api.post(
        "/reviews/",
        reviewData
      );


      setSuccessMessage(
        "Thank you! Your review has been submitted " +
        "and is waiting for approval."
      );


      setFormData({
        customer_name: "",
        rating: 5,
        comment: "",
      });

    } catch (err) {
      console.error(
        "Review submission error:",
        err
      );


      setFormError(
        getApiErrorMessage(err)
      );

    } finally {
      setSubmitting(false);
    }
  };


  // =====================================================
  // STAR DISPLAY
  // =====================================================

  const renderStars = (rating) => {
    const safeRating = Math.max(
      0,
      Math.min(
        5,
        Number(rating)
      )
    );

    return (
      "★".repeat(safeRating) +
      "☆".repeat(5 - safeRating)
    );
  };


  // =====================================================
  // PAGE UI
  // =====================================================

  return (
    <section className="reviews-section">

      <div className="reviews-container">

        {/* REVIEWS HEADING */}

        <div className="reviews-heading">

          <span>
            CUSTOMER REVIEWS
          </span>

          <h2>
            What Our Customers Say
          </h2>

          <p>
            See what customers say about their
            experience with Lovely Mobi Care.
          </p>

        </div>


        {/* LOADING */}

        {loading && (
          <div className="reviews-message">
            Loading reviews...
          </div>
        )}


        {/* REVIEWS LOAD ERROR */}

        {!loading && error && (
          <div
            className="reviews-message reviews-error"
          >
            {error}
          </div>
        )}


        {/* NO REVIEWS */}

        {!loading &&
          !error &&
          reviews.length === 0 && (

          <div className="reviews-empty">

            <div className="reviews-empty-icon">
              ⭐
            </div>

            <h3>
              No reviews yet
            </h3>

            <p>
              Customer reviews will appear here
              after approval.
            </p>

          </div>
        )}


        {/* APPROVED REVIEWS */}

        {!loading &&
          !error &&
          reviews.length > 0 && (

          <div className="reviews-grid">

            {reviews.map((review) => (

              <article
                className="review-card"
                key={review.id}
              >

                <div className="review-stars">
                  {renderStars(
                    review.rating
                  )}
                </div>


                <p className="review-comment">
                  “{review.comment}”
                </p>


                <div className="review-customer">

                  <div className="review-avatar">

                    {review.customer_name
                      ?.charAt(0)
                      .toUpperCase()}

                  </div>


                  <div>

                    <strong>
                      {review.customer_name}
                    </strong>

                    <small>
                      Customer Review
                    </small>

                  </div>

                </div>

              </article>

            ))}

          </div>
        )}


        {/* WRITE REVIEW */}

        <div className="write-review-section">

          <div className="write-review-heading">

            <span>
              SHARE YOUR EXPERIENCE
            </span>

            <h2>
              Write a Review
            </h2>

            <p>
              Had a good experience with Lovely
              Mobi Care? We would love to hear
              from you.
            </p>

          </div>


          <form
            className="review-form"
            onSubmit={handleSubmit}
          >

            {/* SUCCESS MESSAGE */}

            {successMessage && (

              <div className="review-success">
                ✓ {successMessage}
              </div>

            )}


            {/* FORM ERROR */}

            {formError && (

              <div className="review-form-error">
                {formError}
              </div>

            )}


            {/* CUSTOMER NAME */}

            <div className="review-form-group">

              <label htmlFor="review-customer-name">
                Your Name *
              </label>

              <input
                id="review-customer-name"
                type="text"
                name="customer_name"
                value={formData.customer_name}
                onChange={handleChange}
                placeholder="Enter your name"
                minLength="2"
                maxLength="150"
                autoComplete="name"
                required
              />

            </div>


            {/* RATING */}

            <div className="review-form-group">

              <label>
                Your Rating *
              </label>


              <div className="rating-selector">

                {[1, 2, 3, 4, 5].map(
                  (rating) => (

                    <button
                      key={rating}
                      type="button"
                      className={
                        rating <=
                        formData.rating
                          ? "rating-star selected"
                          : "rating-star"
                      }
                      onClick={() =>
                        handleRating(rating)
                      }
                      aria-label={
                        `${rating} star rating`
                      }
                    >
                      ★
                    </button>

                  )
                )}

              </div>


              <small className="selected-rating">

                {formData.rating} out of 5 stars

              </small>

            </div>


            {/* REVIEW COMMENT */}

            <div className="review-form-group">

              <label htmlFor="review-comment">
                Your Review *
              </label>

              <textarea
                id="review-comment"
                name="comment"
                value={formData.comment}
                onChange={handleChange}
                rows="5"
                placeholder="Tell us about your experience..."
                minLength="5"
                maxLength="2000"
                required
              />

            </div>


            {/* SUBMIT BUTTON */}

            <button
              type="submit"
              className="submit-review-button"
              disabled={submitting}
            >

              {submitting
                ? "Submitting..."
                : "Submit Review"}

            </button>

          </form>

        </div>

      </div>

    </section>
  );
}


export default Reviews;
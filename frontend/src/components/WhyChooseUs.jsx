import "./WhyChooseUs.css";

function WhyChooseUs() {
  const features = [
    {
      icon: "🛠️",
      title: "Expert Technicians",
      description:
        "Professional care for mobile repairs with attention to every detail.",
    },
    {
      icon: "✓",
      title: "Quality Parts",
      description:
        "Reliable replacement parts selected for quality and performance.",
    },
    {
      icon: "₹",
      title: "Affordable Pricing",
      description:
        "Clear and competitive pricing for mobile sales and repair services.",
    },
    {
      icon: "🤝",
      title: "Customer Support",
      description:
        "Friendly assistance before, during, and after your mobile service.",
    },
  ];

  return (
    <section className="why-choose-section">
      <div className="why-choose-container">
        <div className="why-choose-heading">
          <span>WHY CHOOSE US</span>

          <h2>Mobile Care You Can Rely On</h2>

          <p>
            From mobile sales to professional repair services,
            Lovely Mobi Care is focused on quality, value, and
            customer satisfaction.
          </p>
        </div>

        <div className="why-choose-grid">
          {features.map((feature) => (
            <article
              className="why-choose-card"
              key={feature.title}
            >
              <div className="why-choose-icon">
                {feature.icon}
              </div>

              <h3>{feature.title}</h3>

              <p>{feature.description}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

export default WhyChooseUs;
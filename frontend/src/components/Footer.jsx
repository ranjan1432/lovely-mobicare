import "./Footer.css";

function Footer() {
  return (
    <footer className="footer">
      <div className="container">
        <p>
          © {new Date().getFullYear()} Lovely Mobi Care. All rights reserved.
        </p>
      </div>
    </footer>
  );
}

export default Footer;
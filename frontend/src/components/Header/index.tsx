import "./style.css";
import { Link } from "react-router";

interface HeaderProps {
  buttonText: string;
  onButtonClicked: () => void;
}

const Header = ({ buttonText, onButtonClicked }: HeaderProps) => {
  return (
    <header className="site-header">
      <Link
        to="/"
        className="brand-name"
        aria-label="LeilõesEliteDev - página inicial"
      >
        LeilõesEliteDev
      </Link>

      <button className="login-button" type="button" onClick={onButtonClicked}>
        {buttonText}
      </button>
    </header>
  );
};

export default Header;

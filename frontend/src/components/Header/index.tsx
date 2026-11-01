import "./style.css";

const Header = () => {
  return (
    <header className="site-header">
      <a className="brand-name" href="#" aria-label="LeilõesEliteDev - página inicial">
        LeilõesEliteDev
      </a>
      <button className="login-button" type="button">Entrar</button>
    </header>
  );
};

export default Header;

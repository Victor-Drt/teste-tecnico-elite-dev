import { useState, type FormEvent } from "react";
import { Link } from "react-router";
import heroLoginIllustration from "../../assets/login-page-woman.svg";
import "./styles.css";
import { IoEyeOutline, IoEyeSharp } from "react-icons/io5";

const LoginPage = () => {
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
  };

  return (
    <main className="login-page">
      <section className="login-hero" aria-label="Sobre a plataforma">
        <p className="login-hero__message">
          Comprar e vender obras de arte nunca esteve tão fácil.
        </p>
        <img
          className="login-hero__illustration"
          src={heroLoginIllustration}
          alt="Mulher escalando uma obra de arte"
        />
      </section>

      <section className="login-panel" aria-labelledby="login-title">
        <div className="login-content">
          <Link
            className="login-brand"
            to="/"
            aria-label="LeilõesEliteDev - início"
          >
            LeilõesEliteDev
          </Link>

          <h1 className="login-title" id="login-title">
            Bem-vindo de volta
          </h1>
          <p className="login-description">
            Entre na sua conta para continuar.
          </p>

          <form className="login-form" onSubmit={handleSubmit}>
            <div className="login-field">
              <label htmlFor="email">E-mail</label>
              <input
                autoComplete="email"
                id="email"
                name="email"
                placeholder="seuemail@exemplo.com"
                required
                type="email"
              />
            </div>

            <div className="login-field">
              <label htmlFor="password">Senha</label>
              <div className="login-password-input">
                <input
                  autoComplete="current-password"
                  id="password"
                  name="password"
                  placeholder="Digite sua senha"
                  required
                  type={isPasswordVisible ? "text" : "password"}
                />
                <button
                  aria-label={
                    isPasswordVisible ? "Ocultar senha" : "Mostrar senha"
                  }
                  aria-pressed={isPasswordVisible}
                  className="login-password-toggle"
                  onClick={() => setIsPasswordVisible((visible) => !visible)}
                  type="button"
                >
                  {isPasswordVisible ? <IoEyeSharp /> : <IoEyeOutline />}
                </button>
              </div>
            </div>

            <button className="login-submit" type="submit">
              Entrar
            </button>
          </form>

          <p className="login-signup">
            Você é novo por aqui? <Link to="/cadastro">Crie uma Conta</Link>
          </p>
        </div>
      </section>
    </main>
  );
};

export default LoginPage;

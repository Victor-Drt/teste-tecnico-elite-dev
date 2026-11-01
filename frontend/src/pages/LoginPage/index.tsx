import { useState, type FormEvent } from "react";
import { Link } from "react-router";
import heroLoginIllustration from "../../assets/login-page-woman.svg";
import "./styles.css";

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
                  {isPasswordVisible ? (
                    <svg aria-hidden="true" fill="none" viewBox="0 0 24 24">
                      <path
                        d="M3 3l18 18M10.6 10.6a2 2 0 002.8 2.8M9.9 5.2A10.7 10.7 0 0112 5c5.5 0 9 7 9 7a15.7 15.7 0 01-3.1 3.8M6.2 6.2C3.9 7.7 3 12 3 12s3.5 7 9 7a9.7 9.7 0 004.1-.9"
                        stroke="currentColor"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="1.8"
                      />
                    </svg>
                  ) : (
                    <svg aria-hidden="true" fill="none" viewBox="0 0 24 24">
                      <path
                        d="M3 12s3.5-7 9-7 9 7 9 7-3.5 7-9 7-9-7-9-7z"
                        stroke="currentColor"
                        strokeLinejoin="round"
                        strokeWidth="1.8"
                      />
                      <circle
                        cx="12"
                        cy="12"
                        r="2.5"
                        stroke="currentColor"
                        strokeWidth="1.8"
                      />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            <button className="login-submit" type="submit">
              Entrar
            </button>
          </form>

          <p className="login-signup">
            Você é novo por aqui? <Link to="/register">Crie uma Conta</Link>
          </p>
        </div>
      </section>
    </main>
  );
};

export default LoginPage;

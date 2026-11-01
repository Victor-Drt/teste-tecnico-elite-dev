import { Link, useNavigate } from "react-router";
import heroRegisterIllustration from "../../assets/register-page-man-join.svg";
import { useState, type FormEvent } from "react";
import { IoEyeOutline, IoEyeSharp } from "react-icons/io5";
import "./styles.css";

const RegisterPage = () => {
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    navigate("/vitrine");
  };

  return (
    <main className="register-page">
      <section className="register-hero">
        <img
          className="register-hero__illustration"
          src={heroRegisterIllustration}
          alt="Homem fazendo joinha"
        />
        <p className="register-hero__message">
          Comprar e vender obras de arte nunca esteve tão fácil.
        </p>
      </section>
      <section className="register-panel" aria-labelledby="register-title">
        <div className="register-content">
          <Link
            className="register-brand"
            to="/"
            aria-label="LeilõesEliteDev - início"
          >
            LeilõesEliteDev
          </Link>

          <h1 className="register-title" id="register-title">
            Olá, bem-vindo!
          </h1>
          <p className="register-description">Cadastre-se para iniciar.</p>
          <form className="register-form" onSubmit={handleSubmit}>
            <div className="register-field">
              <label htmlFor="name">Name</label>
              <input
                id="name"
                name="name"
                placeholder="Jhon Doe"
                required
                type="text"
              />
            </div>

            <div className="register-field">
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

            <div className="register-field">
              <label htmlFor="password">Senha</label>
              <div className="register-password-input">
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
                  className="register-password-toggle"
                  onClick={() => setIsPasswordVisible((visible) => !visible)}
                  type="button"
                >
                  {isPasswordVisible ? <IoEyeSharp /> : <IoEyeOutline />}
                </button>
              </div>
            </div>

            <div className="register-field">
              <label htmlFor="role">Quero:</label>
              <div>
                <input type="radio" name="role" id="licitante" />
                <label htmlFor="licitante">Comprar</label>
              </div>
              <div>
                <input type="radio" name="role" id="leiloeiro" />
                <label htmlFor="leiloeiro">Vender</label>
              </div>
            </div>

            <button className="register-submit" type="submit">
              Cadastrar
            </button>
          </form>

          <p className="register-signin">
            Já tem uma conta? <Link to="/login">Entrar</Link>
          </p>
        </div>
      </section>
    </main>
  );
};

export default RegisterPage;

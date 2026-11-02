import axios from "axios";
import { Link, useNavigate } from "react-router";
import heroRegisterIllustration from "../../assets/register-page-man-join.svg";
import { useState, type FormEvent } from "react";
import { IoEyeOutline, IoEyeSharp } from "react-icons/io5";
import type { UserRole } from "../../types/usuarios";
import { register } from "../../services/usuarios";
import "./styles.css";

const RegisterPage = () => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole | "">("");
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!role) {
      setErrorMessage("Selecione se deseja comprar ou vender.");
      return;
    }

    setErrorMessage("");
    setIsSubmitting(true);

    try {
      await register({ nome: name, email, senha: password, papel: role });
      navigate("/login", {
        replace: true,
        state: { registrationSuccess: true },
      });
    } catch (error) {
      if (axios.isAxiosError<{ detail?: string }>(error)) {
        const detail = error.response?.data?.detail;
        setErrorMessage(
          (typeof detail === "string" && detail) ??
            "Não foi possível conectar ao serviço. Tente novamente.",
        );
      } else {
        setErrorMessage("Ocorreu um erro inesperado ao criar a conta.");
      }
    } finally {
      setIsSubmitting(false);
    }
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
              <label htmlFor="name">Nome</label>
              <input
                autoComplete="name"
                id="name"
                name="name"
                placeholder="Seu nome completo"
                required
                type="text"
                value={name}
                onChange={(event) => setName(event.target.value)}
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
                value={email}
                onChange={(event) => setEmail(event.target.value)}
              />
            </div>

            <div className="register-field">
              <label htmlFor="password">Senha</label>
              <div className="register-password-input">
                <input
                  autoComplete="new-password"
                  id="password"
                  name="password"
                  placeholder="Digite sua senha"
                  required
                  type={isPasswordVisible ? "text" : "password"}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
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

            <fieldset className="register-role">
              <legend>Quero:</legend>
              <label className="register-role__option" htmlFor="licitante">
                <input
                  checked={role === "licitante"}
                  id="licitante"
                  name="role"
                  onChange={() => setRole("licitante")}
                  required
                  type="radio"
                  value="licitante"
                />
                Comprar
              </label>
              <label className="register-role__option" htmlFor="leiloeiro">
                <input
                  checked={role === "leiloeiro"}
                  id="leiloeiro"
                  name="role"
                  onChange={() => setRole("leiloeiro")}
                  required
                  type="radio"
                  value="leiloeiro"
                />
                Vender
              </label>
            </fieldset>

            {errorMessage && (
              <p className="register-error" role="alert">
                {errorMessage}
              </p>
            )}

            <button
              className="register-submit"
              disabled={isSubmitting}
              type="submit"
            >
              {isSubmitting ? "Cadastrando..." : "Cadastrar"}
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

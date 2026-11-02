import axios from "axios";
import { useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router";
import heroLoginIllustration from "../../assets/login-page-woman.svg";
import "./styles.css";
import { IoEyeOutline, IoEyeSharp } from "react-icons/io5";
import { login } from "../../services/auth";
import { fetchUser } from "../../services/usuarios";

const DEFAULT_REDIRECT_PATH = "/vitrine";

function getRedirectPath(state: unknown): string {
  if (
    typeof state !== "object" ||
    state === null ||
    !("from" in state) ||
    typeof state.from !== "object" ||
    state.from === null ||
    !("pathname" in state.from) ||
    typeof state.from.pathname !== "string"
  ) {
    return DEFAULT_REDIRECT_PATH;
  }

  const pathname = state.from.pathname;
  return pathname.startsWith("/") && !pathname.startsWith("//")
    ? pathname
    : DEFAULT_REDIRECT_PATH;
}

const LoginPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const requestedPath = getRedirectPath(location.state);
  const registrationSuccess =
    typeof location.state === "object" &&
    location.state !== null &&
    "registrationSuccess" in location.state &&
    location.state.registrationSuccess === true;
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setErrorMessage("");
    setIsSubmitting(true);

    try {
      await login(email, password);
      const user = await fetchUser();
      const destination =
        user.papel === "leiloeiro"
          ? "/painel-leiloeiro"
          : requestedPath === "/painel-leiloeiro"
            ? "/vitrine"
            : requestedPath;
      navigate(destination, { replace: true });
    } catch (error) {
      if (axios.isAxiosError<{ detail?: string }>(error)) {
        setErrorMessage(
          error.response?.data?.detail ??
            "Não foi possível conectar ao serviço. Tente novamente.",
        );
      } else {
        setErrorMessage("Ocorreu um erro inesperado ao entrar.");
      }
    } finally {
      setIsSubmitting(false);
    }
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

          {registrationSuccess && (
            <p className="login-success" role="status">
              Cadastro realizado com sucesso. Entre com sua conta.
            </p>
          )}

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
                onChange={(e) => setEmail(e.target.value)}
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
                  onChange={(e) => setPassword(e.target.value)}
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

            {errorMessage && (
              <p className="login-error" role="alert">
                {errorMessage}
              </p>
            )}

            <button
              className="login-submit"
              disabled={isSubmitting}
              type="submit"
            >
              {isSubmitting ? "Entrando..." : "Entrar"}
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

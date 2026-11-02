import { useEffect, useState } from "react";
import { Link, NavLink, useNavigate } from "react-router";
import { IoChevronDownOutline, IoWalletOutline } from "react-icons/io5";
import type { User } from "../../types/usuarios";
import type { Wallet } from "../../types/carteiras";
import { logout } from "../../services/auth";
import { fetchWallet } from "../../services/carteiras";
import "./styles.css";

interface NavbarProps {
  user: User;
}

function getUserInitials(name: string): string {
  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toLocaleUpperCase() ?? "")
    .join("");
}

const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

const Navbar = ({ user }: NavbarProps) => {
  const navigate = useNavigate();
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [wallet, setWallet] = useState<Wallet | null>(null);
  const [walletError, setWalletError] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [logoutError, setLogoutError] = useState("");

  useEffect(() => {
    if (user.papel !== "licitante") {
      return;
    }

    let isCurrent = true;
    fetchWallet()
      .then((userWallet) => {
        if (isCurrent) {
          setWallet(userWallet);
        }
      })
      .catch(() => {
        if (isCurrent) {
          setWalletError(true);
        }
      });

    return () => {
      isCurrent = false;
    };
  }, [user.papel]);

  const handleLogout = async () => {
    setLogoutError("");
    setIsLoggingOut(true);

    try {
      await logout();
      navigate("/login", { replace: true });
    } catch {
      setLogoutError("Não foi possível encerrar sua sessão. Tente novamente.");
    } finally {
      setIsLoggingOut(false);
    }
  };

  return (
    <header className="auction-navbar">
      <Link
        aria-label="LeilõesEliteDev - início"
        className="auction-navbar__brand"
        to={user.papel === "leiloeiro" ? "/painel-leiloeiro" : "/vitrine"}
      >
        LeilõesEliteDev
      </Link>

      <nav aria-label="Navegação principal" className="auction-navbar__links">
        {user.papel === "leiloeiro" ? (
          <>
            <NavLink
              className={({ isActive }) =>
                `auction-navbar__link${isActive ? " is-active" : ""}`
              }
              to="/painel-leiloeiro"
            >
              Meus Lotes
            </NavLink>
            <NavLink
              className={({ isActive }) =>
                `auction-navbar__link${isActive ? " is-active" : ""}`
              }
              to="/itens"
            >
              Itens
            </NavLink>
          </>
        ) : (
          <>
            <NavLink
              className={({ isActive }) =>
                `auction-navbar__link${isActive ? " is-active" : ""}`
              }
              to="/vitrine"
            >
              Vitrine
            </NavLink>
            <NavLink
              className={({ isActive }) =>
                `auction-navbar__link${isActive ? " is-active" : ""}`
              }
              to="/carteira"
            >
              Carteira
            </NavLink>
            <NavLink
              className={({ isActive }) =>
                `auction-navbar__link${isActive ? " is-active" : ""}`
              }
              to="/arremates"
            >
              Meus Arremates
            </NavLink>
          </>
        )}
      </nav>

      <div className="auction-navbar__account">
        <button
          aria-expanded={isProfileOpen}
          aria-label={`Perfil de ${user.nome}`}
          className="auction-navbar__profile"
          onClick={() => setIsProfileOpen((open) => !open)}
          type="button"
        >
          <span>{getUserInitials(user.nome)}</span>
          <IoChevronDownOutline aria-hidden="true" />
        </button>

        {isProfileOpen && (
          <section
            aria-label="Informações da conta"
            className="account-popover"
          >
            <div className="account-popover__identity">
              <span className="account-popover__avatar">
                {getUserInitials(user.nome)}
              </span>
              <div>
                <strong>{user.nome}</strong>
                <span>{user.email}</span>
              </div>
            </div>

            {user.papel === "licitante" && (
              <div className="account-popover__balance">
                <span>
                  <IoWalletOutline aria-hidden="true" />
                  Saldo disponível
                </span>
                <strong>
                  {wallet
                    ? currencyFormatter.format(Number(wallet.saldo_disponivel))
                    : walletError
                      ? "Indisponível"
                      : "Carregando..."}
                </strong>
              </div>
            )}

            {logoutError && (
              <p className="account-popover__error" role="alert">
                {logoutError}
              </p>
            )}

            <button
              className="account-popover__logout"
              disabled={isLoggingOut}
              onClick={handleLogout}
              type="button"
            >
              {isLoggingOut ? "Saindo..." : "Sair"}
            </button>
          </section>
        )}
      </div>
    </header>
  );
};

export default Navbar;

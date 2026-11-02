import axios from "axios";
import { useEffect, useState } from "react";
import { Navigate, Outlet, useLocation } from "react-router";
import { fetchUser } from "../services/usuarios";
import type { User } from "../types/usuarios";

type AuthState =
  | { status: "checking" }
  | { status: "authenticated"; user: User }
  | { status: "unauthenticated" }
  | { status: "error" };

const PrivateRoute = () => {
  const location = useLocation();
  const [authState, setAuthState] = useState<AuthState>({ status: "checking" });
  const [retryCount, setRetryCount] = useState(0);

  const handleRetry = () => {
    setAuthState({ status: "checking" });
    setRetryCount((count) => count + 1);
  };

  useEffect(() => {
    let isCurrent = true;

    fetchUser()
      .then((authenticatedUser) => {
        if (isCurrent) {
          setAuthState({ status: "authenticated", user: authenticatedUser });
        }
      })
      .catch((error: unknown) => {
        if (!isCurrent) {
          return;
        }
        if (axios.isAxiosError(error) && error.response?.status === 401) {
          setAuthState({ status: "unauthenticated" });
          return;
        }

        setAuthState({ status: "error" });
      });

    return () => {
      isCurrent = false;
    };
  }, [retryCount]);

  if (authState.status === "checking") {
    return (
      <main aria-busy="true" className="auth-status">
        Verificando sua sessão...
      </main>
    );
  }

  if (authState.status === "unauthenticated") {
    return (
      <Navigate
        to="/login"
        replace
        state={{ from: location }}
      />
    );
  }

  if (authState.status === "error") {
    return (
      <main className="auth-status" role="alert">
        <p>Não foi possível verificar sua sessão.</p>
        <button type="button" onClick={handleRetry}>
          Tentar novamente
        </button>
      </main>
    );
  }

  return <Outlet context={authState.user} />;
};

export default PrivateRoute;

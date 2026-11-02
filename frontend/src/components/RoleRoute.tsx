import { Navigate, Outlet, useOutletContext } from "react-router";
import type { User, UserRole } from "../types/usuarios";

interface RoleRouteProps {
  role: UserRole;
  redirectTo: string;
}

const RoleRoute = ({ role, redirectTo }: RoleRouteProps) => {
  const user = useOutletContext<User>();

  if (user.papel !== role) {
    return <Navigate replace to={redirectTo} />;
  }

  return <Outlet context={user} />;
};

export default RoleRoute;

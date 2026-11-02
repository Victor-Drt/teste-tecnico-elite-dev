import { Outlet, useOutletContext } from "react-router";
import type { User } from "../../types/usuarios";

function AppLayout() {
  const user = useOutletContext<User>();

  return <Outlet context={user} />;
}

export default AppLayout;

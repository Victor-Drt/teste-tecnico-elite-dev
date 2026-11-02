import { Outlet, useOutletContext } from "react-router";
import type { User } from "../../types/usuarios";
import Navbar from "../../components/Navbar";

function AppLayout() {
  const user = useOutletContext<User>();

  return (
    <>
      <Navbar user={user} />
      <Outlet context={user} />
    </>
  );
}

export default AppLayout;

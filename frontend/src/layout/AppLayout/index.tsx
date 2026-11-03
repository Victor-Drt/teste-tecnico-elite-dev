import { Outlet, useOutletContext } from "react-router";
import Navbar from "../../components/Navbar";
import { CarteiraProvider } from "../../context/CarteiraContext";
import type { User } from "../../types/usuarios";

function AppLayout() {
  const user = useOutletContext<User>();

  return (
    <CarteiraProvider user={user}>
      <Navbar user={user} />
      <Outlet context={user} />
    </CarteiraProvider>
  );
}

export default AppLayout;

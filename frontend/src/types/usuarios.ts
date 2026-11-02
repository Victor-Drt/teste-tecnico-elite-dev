type UserRole = "licitante" | "leiloeiro";

interface User {
  id: number;
  nome: string;
  email: string;
  papel: UserRole;
}

interface CreateUserData {
  nome: string;
  email: string;
  senha: string;
  papel: UserRole;
}

export type { User, UserRole, CreateUserData };
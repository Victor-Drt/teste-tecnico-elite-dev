import { useNavigate } from "react-router";
import heroIllustration from "../../assets/home-page-art-museum.png";
import Header from "../../components/Header";
import "./styles.css";

const HomePage = () => {
  const navigate = useNavigate();

  const handleButtonClick = () => {
    navigate("/login", { replace: true });
  };

  return (
    <>
      <Header buttonText="Entrar" onButtonClicked={handleButtonClick} />
      <main className="container">
        <h1>Participe e Organize Leilões</h1>
        <p>Em um ambiente seguro e dinâmico</p>

        <button className="explore-button" type="button" onClick={handleButtonClick}>
          Explorar
        </button>

        <img
          className="hero-illustration"
          src={heroIllustration}
          alt="Ilustração de uma pessoa observando obras de arte"
        />
      </main>
    </>
  );
};

export default HomePage;

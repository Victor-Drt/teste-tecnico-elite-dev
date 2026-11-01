import heroIllustration from "../../assets/home-page-art-museum.png"
import Header from "../../components/Header";
import "./styles.css";

const HomePage = () => {
  return (
    <>
      <Header />
      <main className="container">
        <h1>Participe e Organize Leilões</h1>
        <p>Em um ambiente seguro e dinâmico</p>

        <button className="explore-button" type="button">Explorar</button>

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

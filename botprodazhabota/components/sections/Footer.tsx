import styles from '@/styles/footer.module.scss';

export default function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.inner}>
        <div className={styles.brand}>
          <span className={styles.logo}>Блик</span>
          <p className={styles.tagline}>AI-продавец для VK</p>
        </div>
        <nav className={styles.nav} aria-label="Footer navigation">
          <a href="#features">Возможности</a>
          <a href="#how-it-works">Как работает</a>
          <a href="#cta">Начать</a>
        </nav>
        <p className={styles.copy}>
          © {new Date().getFullYear()} Блик. Все права защищены.
        </p>
      </div>
    </footer>
  );
}

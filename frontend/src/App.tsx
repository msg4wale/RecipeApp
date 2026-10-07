const features = [
  'Chef onboarding and verification',
  'Recipe publishing and plagiarism checks',
  'Social engagement and feed discovery',
  'AI cooking assistant with fallbacks',
];

export default function App() {
  return (
    <main className="app-shell">
      <section className="hero">
        <p className="eyebrow">Recipe App</p>
        <h1>Cook, share, and discover standout recipes.</h1>
        <p className="subtitle">
          A local-first social recipe platform for chefs, home cooks, and AI-assisted culinary guidance.
        </p>
        <div className="feature-list">
          {features.map((feature) => (
            <span key={feature} className="feature-pill">
              {feature}
            </span>
          ))}
        </div>
      </section>
    </main>
  );
}

// src/components/home/HeroSection.jsx

import Button from '../ui/Button';

const BotIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="11" width="18" height="10" rx="2" />
    <circle cx="12" cy="5" r="2" />
    <path d="M12 7v4" />
  </svg>
);

const WorkflowSvg = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="6" height="6" rx="1" />
    <rect x="15" y="15" width="6" height="6" rx="1" />
    <rect x="15" y="3" width="6" height="6" rx="1" />
    <path d="M9 6h3a3 3 0 0 1 3 3v3" />
    <path d="M18 9v6" />
  </svg>
);

const GradientBlob = () => (
  <div className="absolute inset-0 pointer-events-none overflow-hidden" aria-hidden="true">
    <div className="absolute rounded-full"
      style={{
        width: '520px', height: '420px',
        background: 'radial-gradient(circle, rgba(124,58,237,0.55) 0%, transparent 68%)',
        filter: 'blur(72px)', top: '38%', left: '50%',
        transform: 'translate(-50%, -18%)',
      }}
    />
    <div className="absolute rounded-full"
      style={{
        width: '340px', height: '300px',
        background: 'radial-gradient(circle, rgba(249,115,22,0.42) 0%, transparent 68%)',
        filter: 'blur(68px)', bottom: '12%', left: '28%',
      }}
    />
  </div>
);

const HeroSection = () => (
  <section className="relative min-h-screen flex flex-col items-center justify-center text-center px-6 pt-[68px] pb-16 overflow-hidden">
    <GradientBlob />
    <div className="relative z-10 flex flex-col items-center max-w-5xl mx-auto">

      {/* Titre — Inter Bold 96px comme sur la maquette Figma */}
      <h1
        style={{
          fontFamily: "'Inter', sans-serif",
          fontWeight: 700,
          fontSize: '80px',
          lineHeight: 1.0,
          letterSpacing: '-2px',
        }}
        className="text-white mb-6"
      >
        Orchestrez vos agents ia
      </h1>

      <p className="max-w-xl text-white/55 text-base md:text-lg leading-relaxed mb-14">
        Créez, configurez et orchestrez des agents LLM pour collaborer sur des
        projets complexes. Une plateforme intuitive pour démultiplier la puissance de l'IA.
      </p>

      {/* Boutons CTA — fidèles à la maquette */}
      <div className="flex flex-col sm:flex-row items-center gap-4">
        {/* Bouton 1 : Créer un agent → /agents */}
        <Button to="/agents" variant="primary" icon={<BotIcon />}>
          Créer un agent
        </Button>

        {/* Bouton 2 : Créer un workflow → /workflow */}
        <Button to="/workflow" variant="secondary" icon={<WorkflowSvg />}>
          Créer un workflow
        </Button>
      </div>

    </div>
  </section>
);

export default HeroSection;
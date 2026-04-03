import Button from '../ui/Button'
import PageBackground from '../layout/PageBackground'

const BotIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="11" width="18" height="10" rx="2" />
    <circle cx="12" cy="5" r="2" />
    <path d="M12 7v4" />
  </svg>
)

const WorkflowSvg = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="6" height="6" rx="1" />
    <rect x="15" y="15" width="6" height="6" rx="1" />
    <rect x="15" y="3" width="6" height="6" rx="1" />
    <path d="M9 6h3a3 3 0 0 1 3 3v3" />
    <path d="M18 9v6" />
  </svg>
)

const HeroSection = () => (
  <section className="relative min-h-screen flex flex-col items-center justify-center text-center px-6 pt-[68px] pb-16 overflow-hidden">
    <PageBackground />
    <div className="relative z-10 flex flex-col items-center max-w-5xl mx-auto">

      <h1
        style={{
          fontFamily: "'Inter', sans-serif",
          fontWeight: 700,
          fontSize: '80px',
          lineHeight: 1.0,
          letterSpacing: '-2px',
        }}
        className="text-gray-900 dark:text-white mb-6"
      >
        Orchestrez vos agents ia
      </h1>

      <p className="max-w-xl text-gray-500 dark:text-white/55 text-base md:text-lg leading-relaxed mb-14">
        Créez, configurez et orchestrez des agents LLM pour collaborer sur des
        projets complexes. Une plateforme intuitive pour démultiplier la puissance de l'IA.
      </p>

      <div className="flex flex-col sm:flex-row items-center gap-4">
        <Button to="/agents/create" variant="primary" icon={<BotIcon />}>
          Créer un agent
        </Button>
        <Button to="/workflow" variant="secondary" icon={<WorkflowSvg />}>
          Créer un workflow
        </Button>
      </div>

    </div>
  </section>
)

export default HeroSection

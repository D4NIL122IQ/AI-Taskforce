// src/pages/HomePage.jsx

import NavBar      from '../components/layout/NavBar';
import HeroSection from '../components/home/HeroSection';
import FeatureCard from '../components/home/FeatureCard';
import { Bot, Network, Workflow as WorkflowIcon, Sparkles } from 'lucide-react';

const ICON_PROPS = { size: 26, strokeWidth: 1.6 };

const FEATURE_CARDS = [
  {
    id: 'creation-agents',
    icon: <Bot {...ICON_PROPS} />,
    title: "Création d'agents",
    description: "Définissez des agents spécialistes avec leur rôle, modèle LLM, température et prompt système en quelques clics.",
    highlighted: true,
  },
  {
    id: 'orchestration',
    icon: <Network {...ICON_PROPS} />,
    title: 'Orchestration multi-agents',
    description: "Coordonnez plusieurs agents autour d'un superviseur pour collaborer efficacement sur des tâches complexes.",
  },
  {
    id: 'workflows-visuels',
    icon: <WorkflowIcon {...ICON_PROPS} />,
    title: 'Workflows visuels',
    description: "Construisez vos pipelines par glisser-déposer sur un canvas ReactFlow et visualisez l'exécution en temps réel.",
  },
  {
    id: 'gestion-agents',
    icon: <Sparkles {...ICON_PROPS} />,
    title: 'Gestion Agents',
    description: "Gérez le cycle de vie de vos agents, attachez des documents pour le RAG et consultez les historiques d'exécution.",
  },
];

const HomePage = () => {
  return (
    <div className="min-h-screen bg-[#080808] text-white font-body">
      <NavBar />
      <main>
        <HeroSection />
        <section className="relative z-10 max-w-7xl mx-auto px-6 pb-24">
          <h2 className="sr-only">Fonctionnalités principales</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {FEATURE_CARDS.map(({ id, icon, title, description, highlighted }) => (
              <FeatureCard
                key={id}
                icon={icon}
                title={title}
                description={description}
                highlighted={highlighted}
              />
            ))}
          </div>
        </section>
      </main>
    </div>
  );
};

export default HomePage;
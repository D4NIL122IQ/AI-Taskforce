import { useState } from 'react';
import NavBar from '../components/layout/NavBar';
import Button from '../components/ui/Button';

const MODELS = [
  // Llama
  'llama3.3', 'llama3.2', 'llama3.2:1b', 'llama3.1', 'llama3.1:70b', 'llama3.1:405b', 'llama3',
  // Mistral
  'mistral', 'mistral-large', 'mistral-nemo', 'mistral-openorca', 'mixtral', 'mixtral:8x22b',
  // Gemma
  'gemma3', 'gemma3:27b', 'gemma2', 'gemma2:27b', 'gemma',
  // Phi
  'phi4', 'phi4-mini', 'phi3', 'phi3:medium', 'phi3.5',
  // Qwen
  'qwen2.5', 'qwen2.5:72b', 'qwen2.5-coder', 'qwen2', 'qwen2:72b',
  // DeepSeek
  'deepseek-r1', 'deepseek-r1:70b', 'deepseek-r1:671b', 'deepseek-v3', 'deepseek-coder-v2',
  // Command R
  'command-r', 'command-r-plus',
  // Code
  'codellama', 'codellama:70b', 'starcoder2', 'starcoder2:15b', 'granite-code',
  // Autres
  'nous-hermes2', 'openchat', 'solar', 'vicuna', 'orca-mini',
  'wizardlm2', 'yi', 'stablelm2', 'tinyllama', 'dolphin-mistral',
  // Vision
  'llava', 'llava:13b', 'llava:34b', 'moondream', 'bakllava',
];

const SUPERVISOR_PROMPT =
  "Tu es un agent superviseur. Ton rôle est de coordonner les agents spécialistes, " +
  "de décomposer les tâches complexes, de déléguer les sous-tâches aux bons agents et " +
  "de synthétiser leurs réponses pour produire un résultat final cohérent.";

const AgentPage = () => {
  const [roleType, setRoleType] = useState('autre');
  const [webSearch, setWebSearch] = useState(false);
  const [form, setForm] = useState({
    name: '',
    role: '',
    model: MODELS[0],
    temperature: 0.7,
    maxTokens: 2048,
    systemPrompt: '',
  });

  const handleRoleTypeChange = (type) => {
    setRoleType(type);
    if (type === 'superviseur') {
      setForm((prev) => ({ ...prev, role: 'Superviseur', systemPrompt: SUPERVISOR_PROMPT }));
    } else {
      setForm((prev) => ({ ...prev, role: '', systemPrompt: '' }));
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Agent créé :', { ...form, webSearch });
  };

  return (
    <div className="min-h-screen bg-[#080808] text-white font-body">
      <NavBar />

      <main className="max-w-2xl mx-auto px-6 pt-[100px] pb-24">
        <h1 className="text-3xl font-bold mb-2">Créer un agent</h1>
        <p className="text-white/50 text-sm mb-10">
          Configurez un agent IA avec son rôle, son modèle LLM et son prompt système.
        </p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-6">

          {/* Nom */}
          <div className="flex flex-col gap-1.5">
            <label className="text-sm text-white/70">Nom de l'agent</label>
            <input
              type="text"
              name="name"
              value={form.name}
              onChange={handleChange}
              placeholder="Ex : Analyste financier"
              required
              className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-white/30 focus:outline-none focus:border-white/30 transition-colors"
            />
          </div>

          {/* Rôle */}
          <div className="flex flex-col gap-1.5">
            <label className="text-sm text-white/70">Rôle</label>
            <div className="flex gap-3">
              {['superviseur', 'autre'].map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => handleRoleTypeChange(type)}
                  className={[
                    'flex-1 py-3 rounded-xl text-sm font-medium border transition-colors duration-200 cursor-pointer',
                    roleType === type
                      ? 'bg-violet-600/30 border-violet-500 text-white'
                      : 'bg-white/5 border-white/10 text-white/50 hover:text-white hover:border-white/20',
                  ].join(' ')}
                >
                  {type === 'superviseur' ? 'Superviseur' : 'Personnalisé'}
                </button>
              ))}
            </div>
            {roleType === 'autre' && (
              <input
                type="text"
                name="role"
                value={form.role}
                onChange={handleChange}
                placeholder="Ex : Spécialiste en analyse de données"
                className="mt-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-white/30 focus:outline-none focus:border-white/30 transition-colors"
              />
            )}
          </div>

          {/* Modèle LLM */}
          <div className="flex flex-col gap-1.5">
            <label className="text-sm text-white/70">Modèle LLM</label>
            <select
              name="model"
              value={form.model}
              onChange={handleChange}
              className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-white/30 transition-colors appearance-none cursor-pointer"
            >
              {MODELS.map((m) => (
                <option key={m} value={m} className="bg-[#111]">
                  {m}
                </option>
              ))}
            </select>
          </div>

          {/* Température */}
          <div className="flex flex-col gap-2">
            <label className="text-sm text-white/70">
              Température — <span className="text-white">{form.temperature}</span>
            </label>
            <input
              type="range"
              name="temperature"
              min="0"
              max="1"
              step="0.1"
              value={form.temperature}
              onChange={handleChange}
              className="accent-violet-500 cursor-pointer"
            />
            <div className="flex justify-between text-xs text-white/30">
              <span>Précis</span>
              <span>Créatif</span>
            </div>
          </div>

          {/* Longueur max des réponses */}
          <div className="flex flex-col gap-2">
            <label className="text-sm text-white/70">
              Longueur max des réponses — <span className="text-white">{form.maxTokens} tokens</span>
            </label>
            <input
              type="range"
              name="maxTokens"
              min="256"
              max="8192"
              step="256"
              value={form.maxTokens}
              onChange={handleChange}
              className="accent-violet-500 cursor-pointer"
            />
            <div className="flex justify-between text-xs text-white/30">
              <span>256</span>
              <span>8192</span>
            </div>
          </div>

          {/* Recherche web */}
          <div className="flex items-center justify-between bg-white/5 border border-white/10 rounded-xl px-4 py-3">
            <div className="flex flex-col gap-0.5">
              <span className="text-sm text-white">Recherche web</span>
              <span className="text-xs text-white/40">Permet à l'agent d'effectuer des recherches en ligne</span>
            </div>
            <button
              type="button"
              onClick={() => setWebSearch((v) => !v)}
              className={[
                'relative w-11 h-6 rounded-full transition-colors duration-200 cursor-pointer flex-shrink-0',
                webSearch ? 'bg-violet-600' : 'bg-white/15',
              ].join(' ')}
              aria-pressed={webSearch}
              aria-label="Activer la recherche web"
            >
              <span
                className={[
                  'absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform duration-200',
                  webSearch ? 'translate-x-5' : 'translate-x-0',
                ].join(' ')}
              />
            </button>
          </div>

          {/* Prompt système */}
          <div className="flex flex-col gap-1.5">
            <label className="text-sm text-white/70">
              Prompt système
              {roleType === 'superviseur' && (
                <span className="ml-2 text-xs text-violet-400">généré automatiquement</span>
              )}
            </label>
            <textarea
              name="systemPrompt"
              value={form.systemPrompt}
              onChange={handleChange}
              rows={5}
              readOnly={roleType === 'superviseur'}
              placeholder="Décrivez le comportement et les instructions de l'agent..."
              className={[
                'rounded-xl px-4 py-3 text-sm text-white placeholder-white/30 focus:outline-none transition-colors resize-none border',
                roleType === 'superviseur'
                  ? 'bg-violet-600/10 border-violet-500/30 text-white/70 cursor-default'
                  : 'bg-white/5 border-white/10 focus:border-white/30',
              ].join(' ')}
            />
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium transition-colors duration-200 cursor-pointer"
            >
              Créer l'agent
            </button>
            <Button to="/" variant="secondary">
              Annuler
            </Button>
          </div>

        </form>
      </main>
    </div>
  );
};

export default AgentPage;

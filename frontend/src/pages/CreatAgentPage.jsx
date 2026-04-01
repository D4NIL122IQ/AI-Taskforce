import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import NavBar from '../components/layout/NavBar';
import PageBackground from '../components/layout/PageBackground';
import { UploadCloud, X, FileText } from 'lucide-react';

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

const FieldLabel = ({ children }) => (
  <label className="text-sm text-white/70">{children}</label>
);

const AgentPage = () => {
  const [roleType, setRoleType] = useState('autre');
  const [webSearch, setWebSearch] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [files, setFiles] = useState([]);
  const fileInputRef = useRef(null);

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
    if (name === 'systemPrompt' && roleType === 'superviseur') {
      if (!value.startsWith(SUPERVISOR_PROMPT)) return;
    }
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    const newAgent = { ...form, webSearch, id: crypto.randomUUID() };
    const existing = JSON.parse(localStorage.getItem('agents') || '[]');
    localStorage.setItem('agents', JSON.stringify([...existing, newAgent]));
    navigate('/agents');
  };

  const addFiles = (incoming) => {
    const list = Array.from(incoming);
    setFiles((prev) => {
      const names = new Set(prev.map((f) => f.name));
      return [...prev, ...list.filter((f) => !names.has(f.name))];
    });
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    addFiles(e.dataTransfer.files);
  };

  const handleDragOver = (e) => { e.preventDefault(); setIsDragging(true); };
  const handleDragLeave = () => setIsDragging(false);

  const removeFile = (name) => setFiles((prev) => prev.filter((f) => f.name !== name));

  return (
    <div className="min-h-screen bg-[#080808] text-white font-body">
      <PageBackground />
      <NavBar />

      <main className="max-w-6xl mx-auto px-6 pt-[100px] pb-24">
        <h1 className="text-3xl font-bold mb-2">Créer un agent</h1>
        <p className="text-white/50 text-sm mb-10">
          Configurez un agent IA avec son rôle, son modèle LLM et son prompt système.
        </p>

        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

            {/* ── Colonne 1 ── */}
            <div className="flex flex-col gap-5">

              {/* Nom */}
              <div className="flex flex-col gap-1.5">
                <FieldLabel>Nom de l'agent</FieldLabel>
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

              {/* Modèle LLM */}
              <div className="flex flex-col gap-1.5">
                <FieldLabel>Modèle LLM</FieldLabel>
                <select
                  name="model"
                  value={form.model}
                  onChange={handleChange}
                  className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-white/30 transition-colors appearance-none cursor-pointer"
                >
                  {MODELS.map((m) => (
                    <option key={m} value={m} className="bg-[#111]">{m}</option>
                  ))}
                </select>
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

              {/* Température */}
              <div className="flex flex-col gap-2">
                <FieldLabel>
                  Température — <span className="text-white">{form.temperature}</span>
                </FieldLabel>
                <input
                  type="range"
                  name="temperature"
                  min="0" max="1" step="0.1"
                  value={form.temperature}
                  onChange={handleChange}
                  className="accent-violet-500 cursor-pointer"
                />
                <div className="flex justify-between text-xs text-white/30">
                  <span>Précis</span>
                  <span>Créatif</span>
                </div>
              </div>

              {/* Longueur max */}
              <div className="flex flex-col gap-2">
                <FieldLabel>
                  Longueur max — <span className="text-white">{form.maxTokens} tokens</span>
                </FieldLabel>
                <input
                  type="range"
                  name="maxTokens"
                  min="256" max="8192" step="256"
                  value={form.maxTokens}
                  onChange={handleChange}
                  className="accent-violet-500 cursor-pointer"
                />
                <div className="flex justify-between text-xs text-white/30">
                  <span>256</span>
                  <span>8192</span>
                </div>
              </div>

            </div>

            {/* ── Colonne 2 ── */}
            <div className="flex flex-col gap-5">

              {/* Rôle */}
              <div className="flex flex-col gap-1.5">
                <FieldLabel>Rôle</FieldLabel>
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

              {/* Prompt système */}
              <div className="flex flex-col gap-1.5">
                <FieldLabel>
                  Prompt système
                  {roleType === 'superviseur' && (
                    <span className="ml-2 text-xs text-violet-400">généré automatiquement</span>
                  )}
                </FieldLabel>
                <textarea
                  name="systemPrompt"
                  value={form.systemPrompt}
                  onChange={handleChange}
                  rows={5}
                  placeholder="Décrivez le comportement et les instructions de l'agent..."
                  className="rounded-xl px-4 py-3 text-sm text-white placeholder-white/30 focus:outline-none transition-colors resize-none border bg-white/5 border-white/10 focus:border-white/30"
                />
              </div>

              {/* Zone drag & drop */}
              <div className="flex flex-col gap-1.5 flex-1">
                <FieldLabel>Documents de référence</FieldLabel>
                <div
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onClick={() => fileInputRef.current?.click()}
                  className={[
                    'flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed px-6 py-8 cursor-pointer transition-all duration-200 min-h-[160px]',
                    isDragging
                      ? 'border-violet-500 bg-violet-600/10'
                      : 'border-white/10 bg-white/[0.02] hover:border-white/20 hover:bg-white/5',
                  ].join(' ')}
                >
                  <UploadCloud size={28} className={isDragging ? 'text-violet-400' : 'text-white/30'} />
                  <div className="text-center">
                    <p className="text-sm text-white/50">
                      Glissez vos fichiers ici ou{' '}
                      <span className="text-violet-400 underline underline-offset-2">parcourez</span>
                    </p>
                    <p className="text-xs text-white/25 mt-1">PDF, TXT, MD, JSON — max 10 Mo</p>
                  </div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    className="hidden"
                    onChange={(e) => addFiles(e.target.files)}
                  />
                </div>

                {/* Liste des fichiers */}
                {files.length > 0 && (
                  <ul className="flex flex-col gap-2 mt-1">
                    {files.map((f) => (
                      <li
                        key={f.name}
                        className="flex items-center justify-between bg-white/5 border border-white/10 rounded-xl px-4 py-2.5"
                      >
                        <div className="flex items-center gap-3 min-w-0">
                          <FileText size={15} className="text-violet-400 flex-shrink-0" />
                          <span className="text-sm text-white/70 truncate">{f.name}</span>
                          <span className="text-xs text-white/30 flex-shrink-0">
                            {(f.size / 1024).toFixed(0)} Ko
                          </span>
                        </div>
                        <button
                          type="button"
                          onClick={() => removeFile(f.name)}
                          className="text-white/30 hover:text-white/70 transition-colors ml-3 flex-shrink-0"
                          aria-label={`Supprimer ${f.name}`}
                        >
                          <X size={15} />
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-8 border-t border-white/10 mt-8">
            <button
              type="submit"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium transition-colors duration-200 cursor-pointer"
            >
              Créer l'agent
            </button>
            <button
              type="button"
              onClick={() => navigate('/agents')}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-white/5 border border-white/10 hover:border-white/20 text-white/70 hover:text-white text-sm font-medium transition-all duration-200 cursor-pointer"
            >
              Annuler
            </button>
          </div>

        </form>
      </main>
    </div>
  );
};

export default AgentPage;

const FeatureCard = ({ icon, title, description, highlighted }) => (
  <div
    className={[
      'flex flex-col gap-4 p-6 rounded-2xl border transition-all duration-200',
      highlighted
        ? 'bg-violet-50 border-violet-200 dark:bg-violet-600/10 dark:border-violet-500/30'
        : 'bg-white border-gray-200 hover:border-gray-300 dark:bg-white/[0.03] dark:border-white/10 dark:hover:border-white/20',
    ].join(' ')}
  >
    <div
      className={[
        'w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0',
        highlighted
          ? 'bg-violet-100 text-violet-600 dark:bg-violet-500/20 dark:text-violet-400'
          : 'bg-gray-100 text-gray-500 dark:bg-white/5 dark:text-white/50',
      ].join(' ')}
    >
      {icon}
    </div>
    <h3 className="text-gray-900 dark:text-white font-semibold text-base leading-snug">{title}</h3>
    <p className="text-gray-500 dark:text-white/50 text-sm leading-relaxed">{description}</p>
  </div>
)

export default FeatureCard

const PageBackground = () => (
  <div className="fixed inset-0 pointer-events-none overflow-hidden" aria-hidden="true">
    <div
      className="absolute rounded-full"
      style={{
        width: '520px', height: '420px',
        background: 'radial-gradient(circle, rgba(124,58,237,0.55) 0%, transparent 68%)',
        filter: 'blur(72px)', top: '38%', left: '50%',
        transform: 'translate(-50%, -18%)',
      }}
    />
    <div
      className="absolute rounded-full"
      style={{
        width: '340px', height: '300px',
        background: 'radial-gradient(circle, rgba(249,115,22,0.42) 0%, transparent 68%)',
        filter: 'blur(68px)', bottom: '12%', left: '28%',
      }}
    />
  </div>
)

export default PageBackground

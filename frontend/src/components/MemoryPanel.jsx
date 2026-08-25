export default function MemoryPanel({ memory }) {
  if (!memory) return null
  const failures = memory.common_failures || []
  const updates = memory.prompt_updates || []

  return (
    <section className="card">
      <h2>Memory (learned across runs)</h2>
      <h3>Common failures seen so far</h3>
      {failures.length ? (
        <ul>
          {failures.map((f) => (
            <li key={f}>{f}</li>
          ))}
        </ul>
      ) : (
        <p>None yet.</p>
      )}
      <h3>Prompt guidance learned</h3>
      {updates.length ? (
        <ul>
          {updates.map((u) => (
            <li key={u}>{u}</li>
          ))}
        </ul>
      ) : (
        <p>None yet.</p>
      )}
    </section>
  )
}

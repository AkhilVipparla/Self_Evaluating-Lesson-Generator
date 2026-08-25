export default function RetryHistory({ rejectionLog, retryCount }) {
  return (
    <section className="card">
      <h2>Retry History</h2>
      <p>Total retries used: {retryCount}</p>
      {rejectionLog.length === 0 ? (
        <p>No rejections — the lesson passed on the first attempt.</p>
      ) : (
        rejectionLog.map((entry) => (
          <div key={entry.attempt} className="attempt">
            <h3>Attempt {entry.attempt} — FAILED</h3>
            <ul className="checklist">
              {Object.entries(entry.checks).map(([key, value]) => (
                <li key={key} className={value ? 'pass' : 'fail'}>
                  <span className="badge">{value ? '✓' : '✗'}</span>
                  {key}
                </li>
              ))}
            </ul>
            {entry.reasons.length > 0 && (
              <ul className="reasons">
                {entry.reasons.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            )}
          </div>
        ))
      )}
    </section>
  )
}

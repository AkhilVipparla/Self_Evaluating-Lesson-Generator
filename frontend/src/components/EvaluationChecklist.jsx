const CHECK_LABELS = {
  definition: 'Definition',
  motivation: 'Motivation',
  workflow: 'Workflow',
  example: 'Example',
  simple_language: 'Beginner Language',
  jargon_explained: 'Jargon Explained',
  accuracy: 'Accuracy',
  flow: 'Flow',
  summary: 'Summary',
  length: 'Length',
}

export default function EvaluationChecklist({ evaluation }) {
  if (!evaluation || !evaluation.checks) return null
  const entries = Object.entries(evaluation.checks)

  return (
    <section className="card">
      <h2>Evaluation Report</h2>
      <p className={evaluation.pass ? 'status pass' : 'status fail'}>
        {evaluation.pass ? 'PASS — all checks passed' : 'FAIL — see reasons below'}
      </p>
      <ul className="checklist">
        {entries.map(([key, value]) => (
          <li key={key} className={value ? 'pass' : 'fail'}>
            <span className="badge">{value ? '✓' : '✗'}</span>
            {CHECK_LABELS[key] || key}
          </li>
        ))}
      </ul>
      {evaluation.reasons?.length > 0 && (
        <>
          <h3>Reasons</h3>
          <ul>
            {evaluation.reasons.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </>
      )}
    </section>
  )
}

function renderMarkdown(text) {
  const lines = text.split('\n')
  const blocks = []
  let paragraph = []
  let listItems = []

  const flushParagraph = () => {
    if (paragraph.length) {
      blocks.push(<p key={blocks.length}>{paragraph.join(' ')}</p>)
      paragraph = []
    }
  }
  const flushList = () => {
    if (listItems.length) {
      blocks.push(
        <ul key={blocks.length}>
          {listItems.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>,
      )
      listItems = []
    }
  }

  for (const rawLine of lines) {
    const line = rawLine.trim()
    if (!line) {
      flushParagraph()
      flushList()
      continue
    }
    const h2 = line.match(/^##\s+(.*)/)
    const h1 = line.match(/^#\s+(.*)/)
    const li = line.match(/^[-*]\s+(.*)/)
    if (h2) {
      flushParagraph()
      flushList()
      blocks.push(<h3 key={blocks.length}>{h2[1]}</h3>)
      continue
    }
    if (h1) {
      flushParagraph()
      flushList()
      blocks.push(<h2 key={blocks.length}>{h1[1]}</h2>)
      continue
    }
    if (li) {
      flushParagraph()
      listItems.push(li[1])
      continue
    }
    flushList()
    paragraph.push(line)
  }
  flushParagraph()
  flushList()
  return blocks
}

export default function LessonView({ finalLesson }) {
  if (!finalLesson || !finalLesson.lesson) return null
  return (
    <section className="card">
      <h2>{finalLesson.title}</h2>
      {!finalLesson.passed && (
        <p className="warning">
          This draft did not pass every rubric check within the retry limit. Showing the best
          available attempt.
        </p>
      )}
      <div className="lesson-body">{renderMarkdown(finalLesson.lesson)}</div>
    </section>
  )
}

export default function TopicForm({ topic, setTopic, onSubmit, loading, placeholder }) {
  return (
    <form
      className="topic-form"
      onSubmit={(e) => {
        e.preventDefault()
        onSubmit()
      }}
    >
      <label htmlFor="topic">Topic</label>
      <input
        id="topic"
        type="text"
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
        placeholder={placeholder ? `e.g. ${placeholder}` : 'Enter any topic to teach'}
        disabled={loading}
      />
      <button type="submit" disabled={loading || !topic.trim()}>
        {loading ? 'Generating…' : 'Generate Lesson'}
      </button>
    </form>
  )
}

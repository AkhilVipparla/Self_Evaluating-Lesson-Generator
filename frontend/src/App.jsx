import { useEffect, useState } from 'react'
import './App.css'
import TopicForm from './components/TopicForm'
import LessonView from './components/LessonView'
import EvaluationChecklist from './components/EvaluationChecklist'
import RetryHistory from './components/RetryHistory'
import MemoryPanel from './components/MemoryPanel'
import { fetchExampleTopic, fetchMemory, generateLesson } from './api'

function App() {
  const [topic, setTopic] = useState('')
  const [placeholder, setPlaceholder] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [memory, setMemory] = useState(null)

  useEffect(() => {
    fetchExampleTopic()
      .then((d) => setPlaceholder(d.example_topic))
      .catch(() => {})
    fetchMemory()
      .then(setMemory)
      .catch(() => {})
  }, [])

  const handleSubmit = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await generateLesson(topic.trim())
      setResult(data)
      setMemory(data.memory_updates)
    } catch (err) {
      setError(err.message || 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header>
        <h1>Self-Evaluating Lesson Generator</h1>
        <p>
          Enter any topic. A team of agents plans, writes, evaluates, and improves the lesson
          before showing it to you.
        </p>
      </header>

      <TopicForm
        topic={topic}
        setTopic={setTopic}
        onSubmit={handleSubmit}
        loading={loading}
        placeholder={placeholder}
      />

      {error && <p className="error">{error}</p>}
      {loading && <p className="loading">Planning, generating, evaluating, and improving…</p>}

      {result && (
        <div className="results">
          <LessonView finalLesson={result.final_lesson} />
          <EvaluationChecklist evaluation={result.evaluation} />
          <RetryHistory rejectionLog={result.rejection_log} retryCount={result.retry_count} />
        </div>
      )}

      <MemoryPanel memory={memory} />
    </div>
  )
}

export default App

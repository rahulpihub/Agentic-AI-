import { useState } from 'react'
import axios from 'axios'

function App() {
  const [form, setForm] = useState({
    company_name: '',
    objective: '',
    scope: '',
    partnership_type: '',
  })
  const [draft, setDraft] = useState('')
  type Clause = { clause_id: string; text: string }
  const [clauses, setClauses] = useState<Clause[]>([])     // ← new
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const generateDraft = async () => {
    setLoading(true)
    try {
      const res = await axios.post(
        'http://localhost:8000/api/generate-draft/',
        form
      )
      const result = res.data.result || {}
      setDraft(result.draft_text || '')                    // ← draft_text
      setClauses(result.retrieved_clauses || [])           // ← retrieved_clauses
    } catch (error) {
      alert('Error generating MoU. Please check backend.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-navy-900 to-navy-800 flex items-center justify-center py-12">
      <div className="max-w-7xl w-full ml-[75px] p-8 bg-black rounded-2xl shadow-2xl space-y-8">
        <h1 className="text-4xl font-extrabold text-center text-navy-900 tracking-tight">
          📄 MoU Generator
          <span className="block text-xl font-medium text-orange-500 mt-1">
            Powered by Agentic AI
          </span>
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Company Name */}
          <div className="relative">
            <input
              name="company_name"
              value={form.company_name}
              onChange={handleChange}
              placeholder="Company Name"
              className="w-full p-4 border border-navy-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all duration-300 text-navy-900 placeholder-navy-400 bg-navy-50"
            />
            <label className="absolute -top-0 left-3 bg-navy-50 px-2 text-sm font-medium text-navy-600">
              Company Name
            </label>
          </div>

          {/* Partnership Type */}
          <div className="relative">
            <input
              name="partnership_type"
              value={form.partnership_type}
              onChange={handleChange}
              placeholder="Partnership Type (e.g., Internship)"
              className="w-full p-4 border border-navy-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all duration-300 text-navy-900 placeholder-navy-400 bg-navy-50"
            />
            <label className="absolute -top-0 left-3 bg-navy-50 px-2 text-sm font-medium text-navy-600">
              Partnership Type
            </label>
          </div>

          {/* Objective */}
          <div className="relative col-span-2">
            <textarea
              name="objective"
              value={form.objective}
              onChange={handleChange}
              placeholder="Objective"
              rows={3}
              className="w-full p-4 border border-navy-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all duration-300 text-navy-900 placeholder-navy-400 bg-navy-50 resize-none"
            />
            <label className="absolute -top-0 left-3 bg-navy-50 px-2 text-sm font-medium text-navy-600">
              Objective
            </label>
          </div>

          {/* Scope */}
          <div className="relative col-span-2">
            <textarea
              name="scope"
              value={form.scope}
              onChange={handleChange}
              placeholder="Scope"
              rows={4}
              className="w-full p-4 border border-navy-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all duration-300 text-navy-900 placeholder-navy-400 bg-navy-50 resize-none"
            />
            <label className="absolute -top-0 left-3 bg-navy-50 px-2 text-sm font-medium text-navy-600">
              Scope
            </label>
          </div>
        </div>

        {/* Generate Button */}
        <button
          onClick={generateDraft}
          disabled={loading}
          className="w-full bg-orange-500 hover:bg-orange-600 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <svg
                className="animate-spin h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Generating...
            </>
          ) : (
            'Generate MoU Draft'
          )}
        </button>

        {/* Generated MoU */}
        {draft && (
          <div className="p-6 border border-navy-200 rounded-xl bg-navy-50 space-y-4">
            <h2 className="text-2xl font-semibold text-navy-900">
              Agent 1 - Generated MoU
            </h2>
            <div className="text-navy-800 whitespace-pre-wrap leading-relaxed bg-black p-4 rounded-lg shadow-inner border border-navy-100">
              {draft}
            </div>
          </div>
        )}

        {/* Retrieved Clauses */}
        {clauses.length > 0 && (
          <div className="p-6 border border-navy-200 rounded-xl bg-navy-50 space-y-4">
            <h2 className="text-2xl font-semibold text-navy-900">
              Agent 2 - Suggested Legal Clauses
            </h2>
            <ul className="list-disc list-inside text-navy-800 space-y-1">
              {clauses.map((c) => (
                <li key={c.clause_id}>
                  <strong>[{c.clause_id}]</strong> {c.text}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}

export default App

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
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const generateDraft = async () => {
    setLoading(true)
    try {
      const res = await axios.post('http://localhost:8000/api/generate-draft/', form)
      setDraft(res.data.result) // ✅ fixed from res.data.draft
    } catch (error) {
      alert('Error generating MoU. Please check backend.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold text-center text-blue-700">
        📄 MoU Generator (Agentic AI)
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <input
          className="border p-2 rounded"
          placeholder="Company Name"
          name="company_name"
          value={form.company_name}
          onChange={handleChange}
        />
        <input
          className="border p-2 rounded"
          placeholder="Partnership Type (e.g., Internship)"
          name="partnership_type"
          value={form.partnership_type}
          onChange={handleChange}
        />
        <textarea
          className="border p-2 rounded col-span-2"
          placeholder="Objective"
          rows={2}
          name="objective"
          value={form.objective}
          onChange={handleChange}
        />
        <textarea
          className="border p-2 rounded col-span-2"
          placeholder="Scope"
          rows={3}
          name="scope"
          value={form.scope}
          onChange={handleChange}
        />
      </div>

      <button
        onClick={generateDraft}
        className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded"
        disabled={loading}
      >
        {loading ? 'Generating...' : 'Generate MoU Draft'}
      </button>

      {draft && (
        <div className="mt-6 p-4 border rounded bg-gray-50 whitespace-pre-wrap">
          <h2 className="text-xl font-semibold mb-2">Generated MoU</h2>
          {draft}
        </div>
      )}
    </div>
  )
}

export default App

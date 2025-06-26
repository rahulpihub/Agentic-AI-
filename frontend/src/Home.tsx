import { useState } from 'react'
import axios from 'axios'

export default function Home() {
  const [form, setForm] = useState({
    company_name: '',
    objective: '',
    scope: '',
    partnership_type: '',
    mou_date: '', // 👈 Add this field
  })
  type Clause = { clause_id: string; text: string }
  const [draft, setDraft] = useState('')
  const [clauses, setClauses] = useState<Clause[]>([])
  const [loading, setLoading] = useState(false)
  const [emailsSent, setEmailsSent] = useState<string[]>([])
  const [approvalStatus, setApprovalStatus] = useState<{ [key: string]: string }>({})
  const [overallStatus, setOverallStatus] = useState('')
  const [versionNumber, setVersionNumber] = useState('')
  const [versionDiff, setVersionDiff] = useState('')

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  // Helper Card component
  const Card = ({ title, children }) => (
    <div className="bg-white border border-blue-100 rounded-lg shadow p-6 space-y-4">
      <h2 className="text-xl font-bold text-blue-800">{title}</h2>
      {children}
    </div>
  )

  const generateDraft = async () => {
    setLoading(true)
    try {
      const res = await axios.post('http://localhost:8000/api/generate-draft/', form)
      const result = res.data.result || {}
      setDraft(result.draft_text || '')
      setClauses(result.retrieved_clauses || [])
      setEmailsSent(result.emails_sent || [])
      setApprovalStatus(result.approval_status || {})
      setOverallStatus(result.overall_mou_status || '')
      setVersionNumber(result.version_number || '')
      setVersionDiff(result.version_diff || '')
    } catch (error) {
      alert('Error generating MoU. Please check backend.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-slate-100 max-w-screen items-center justify-center px-10 py-10">
      <div className="w-full max-w-5xl mt-10 bg-white rounded-2xl shadow-2xl p-10 space-y-10 border border-slate-200">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-extrabold text-blue-800">
            MoU Lifecycle Automation
          </h1>
          <p className="text-lg mt-2 text-blue-600 font-medium">
            Powered by Agentic AI
          </p>
        </div>

        {/* Form Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6  text-black-600 font-bold">
          <input
            name="company_name"
            value={form.company_name}
            onChange={handleChange}
            placeholder="Company Name"
            className="w-full p-4 border border-slate-300 rounded-md bg-white text-black placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <select
            name="partnership_type"
            value={form.partnership_type}
            onChange={handleChange}
            className="w-full p-4 border border-slate-300 rounded-md bg-white text-black focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select Partnership Type</option>
            <option value="All">All</option>
            <option value="Internship">Internship</option>
            <option value="Research">Research</option>
          </select>
          <textarea
            name="objective"
            value={form.objective}
            onChange={handleChange}
            placeholder="Objective"
            rows={3}
            className="input-field md:col-span-2 resize-none"
          />
          <textarea
            name="scope"
            value={form.scope}
            onChange={handleChange}
            placeholder="Scope"
            rows={4}
            className="input-field md:col-span-2 resize-none"
          />
          <input
            type="date"
            name="mou_date"
            value={form.mou_date}
            onChange={handleChange}
            min={new Date().toISOString().split("T")[0]} // restrict to future dates
            className="w-full p-4 border  border-slate-300 rounded-md bg-black text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Button */}
        <button
          onClick={generateDraft}
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-300 flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {loading ? (
            <>
              <svg
                className="animate-spin h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
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

        {/* Agent Outputs */}
        {draft && (
          <Card title="Agent 1 - Generated MoU Executed">
            <pre className="text-gray-800 whitespace-pre-wrap bg-gray-100 p-4 pt-10 rounded-md border border-gray-300">
              {draft}
            </pre>
          </Card>
        )}

        {clauses.length > 0 && (
          <Card title="Agent 2 - Suggested Legal Clauses Executed">
            <ul className="list-disc list-inside text-gray-700">
              {clauses.map((c) => (
                <li key={c.clause_id}>
                  <strong>[{c.clause_id}]</strong> {c.text}
                </li>
              ))}
            </ul>
          </Card>
        )}

        {emailsSent.length > 0 && (
          <Card title="Agent 3 - Communication Handler Agent Executed">
            <p className="text-gray-700">
              ✅ Email sent to: <strong>{emailsSent.join(', ')}</strong>
            </p>
          </Card>
        )}

        {overallStatus && (
          <Card title="Agent 4 - Approval Tracker Agent Executed">
            <p className="text-gray-700">
              📝 Overall MoU Status: <strong>{overallStatus}</strong>
            </p>
            <ul className="list-disc list-inside text-gray-700">
              {Object.entries(approvalStatus).map(([email, status]) => (
                <li key={email}>
                  <strong>{email}</strong>: {status}
                </li>
              ))}
            </ul>
          </Card>
        )}

        {versionNumber && (
          <Card title="Agent 5 - Version Control Agent Executed">
            <p className="text-gray-700">📄 Version Number: <strong>{versionNumber}</strong></p>
            <p className="text-gray-700">🆕 Version Diff: <strong>{versionDiff}</strong></p>
          </Card>
        )}
      </div>
    </div>
  )
}





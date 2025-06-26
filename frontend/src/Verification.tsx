import { useEffect, useState } from 'react'
import axios from 'axios'

interface Approval {
    name: string
    email: string
    role: string
    status: string
}

export default function Verification() {
    const [approvals, setApprovals] = useState<Approval[]>([])
    const [updatedStatus, setUpdatedStatus] = useState<{ [email: string]: string }>({})

    useEffect(() => {
        const fetchApprovals = async () => {
            try {
                const res = await axios.get('http://localhost:8000/api/approvals/')
                setApprovals(res.data.approvals || [])
            } catch (err) {
                console.error('Failed to fetch approvals:', err)
            }
        }

        fetchApprovals()
    }, [])

    const handleStatusChange = (email: string, newStatus: string) => {
        setUpdatedStatus((prev) => ({ ...prev, [email]: newStatus }))
    }

    const submitStatusUpdate = async (email: string) => {
        const newStatus = updatedStatus[email]
        if (!newStatus) return alert("Please select a status before submitting.")

        try {
            await axios.post('http://localhost:8000/api/update-approval/', {
                email,
                status: newStatus
            })
            alert(`Status updated for ${email} → ${newStatus}`)
        } catch (err) {
            console.error("Failed to update status:", err)
            alert("Error updating status")
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-white-100">
            <div className="bg-white p-10 rounded-xl shadow-xl border border-blue-200 max-w-3xl w-full">
                <h2 className="text-2xl font-bold text-blue-800 mb-6">Approval Status</h2>
                {approvals.length > 0 ? (
                    <div className="space-y-6">
                        {approvals.map((entry, idx) => (
                            <div key={idx} className="border p-4 rounded-lg text-blue-800 shadow-sm bg-slate-50">
                                <p><strong>Name:</strong> {entry.name}</p>
                                <p><strong>Email:</strong> {entry.email}</p>
                                <p><strong>Role:</strong> {entry.role}</p>
                                <div className="flex items-center gap-4 mt-2">
                                    <label className="font-semibold">Status:</label>
                                    <select
                                        value={updatedStatus[entry.email] || entry.status}
                                        onChange={(e) => handleStatusChange(entry.email, e.target.value)}
                                        className="border border-slate-300 rounded-md p-2 bg-white"
                                    >
                                        <option value="Approved">Approved</option>
                                        <option value="Rejected">Rejected</option>
                                        <option value="Idle">Idle</option>
                                    </select>
                                    <button
                                        onClick={() => submitStatusUpdate(entry.email)}
                                        className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-1 px-4 rounded-md"
                                    >
                                        Submit
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="text-gray-600">Loading approval data...</p>
                )}
            </div>
        </div>
    )
}

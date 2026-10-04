import * as React from "react"
import { ApprovalCard } from "@/components/approvals/approval-card"
import { ScrollArea } from "@/components/ui/scroll-area"

export default async function ApprovalsPage() {
  let approvals: any[] = []
  let fetchError = false
  
  try {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"
    const res = await fetch(`${baseUrl}/approvals/`, { cache: 'no-store' })
    if (res.ok) {
      approvals = await res.json()
    } else {
      fetchError = true
    }
  } catch (error) {
    console.error("Failed to fetch approvals", error)
    fetchError = true
  }

  return (
    <div className="flex h-full flex-col">
      <div className="p-6 pb-4">
        <h1 className="text-2xl font-bold tracking-tight">Approvals Inbox</h1>
        <p className="text-sm text-gray-500 mt-1">Review and manage pending requests.</p>
      </div>
      <ScrollArea className="flex-1 px-6 pb-6">
        {fetchError ? (
          <div className="text-red-500 py-6">Failed to load approvals. Please try again later.</div>
        ) : approvals.length === 0 ? (
          <div className="text-gray-500 py-6">No pending approvals required at this time.</div>
        ) : (
          <div className="grid gap-4 max-w-3xl">
            {approvals.map((approval) => (
              <ApprovalCard key={approval.id} {...approval} />
            ))}
          </div>
        )}
      </ScrollArea>
    </div>
  )
}

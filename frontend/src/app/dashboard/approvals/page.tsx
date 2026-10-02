import * as React from "react"
import { ApprovalCard } from "@/components/approvals/approval-card"
import { ScrollArea } from "@/components/ui/scroll-area"

const mockApprovals = [
  {
    id: "a1",
    title: "Budget Increase for Q3 Marketing",
    requester: "Alice Smith",
    date: "2026-10-01",
    details: "Requesting an additional $50,000 to cover expanded ad spend for the upcoming holiday campaign. This has been discussed with the marketing director and aligns with our Q3 growth goals.",
  },
  {
    id: "a2",
    title: "New Hire: Senior Developer",
    requester: "Bob Johnson",
    date: "2026-10-02",
    details: "Approval to extend an offer to candidate #42 for the Senior Backend Developer role. Compensation package is within the approved band.",
  },
  {
    id: "a3",
    title: "Vendor Contract Renewal: Cloud Services",
    requester: "Charlie Davis",
    date: "2026-09-28",
    details: "Annual renewal for our cloud infrastructure provider. The new contract includes a 5% volume discount over the previous year.",
  },
]

export default function ApprovalsPage() {
  return (
    <div className="flex h-full flex-col">
      <div className="p-6 pb-4">
        <h1 className="text-2xl font-bold tracking-tight">Approvals Inbox</h1>
        <p className="text-sm text-gray-500 mt-1">Review and manage pending requests.</p>
      </div>
      <ScrollArea className="flex-1 px-6 pb-6">
        <div className="grid gap-4 max-w-3xl">
          {mockApprovals.map((approval) => (
            <ApprovalCard key={approval.id} {...approval} />
          ))}
        </div>
      </ScrollArea>
    </div>
  )
}

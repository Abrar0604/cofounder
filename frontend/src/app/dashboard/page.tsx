import * as React from "react"
import { VentureSummary } from "@/components/dashboard/venture-summary"

export default function DashboardPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold tracking-tight mb-6">Dashboard</h1>
      <div className="grid gap-6">
        <VentureSummary />
      </div>
    </div>
  )
}

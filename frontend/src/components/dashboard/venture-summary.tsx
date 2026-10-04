import * as React from "react"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

export async function VentureSummary() {
  let ventures: any[] = []
  try {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"
    const res = await fetch(`${baseUrl}/ventures/`, { cache: 'no-store' })
    if (res.ok) {
      ventures = await res.json()
    }
  } catch (error) {
    console.error("Failed to fetch ventures", error)
  }

  return (
    <Card className="rounded-none shadow-none">
      <CardHeader>
        <CardTitle>Venture Summary</CardTitle>
        <CardDescription>Overview of all current ventures and their status.</CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Budget</TableHead>
              <TableHead className="text-right">Progress</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {ventures.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center text-gray-500 py-6">
                  No ventures found. Start a new project in the chat!
                </TableCell>
              </TableRow>
            ) : (
              ventures.map((venture) => (
                <TableRow key={venture.id}>
                  <TableCell className="font-medium">{venture.name}</TableCell>
                  <TableCell>
                    <Badge variant={venture.status === "Active" ? "default" : venture.status === "Pending" ? "secondary" : "outline"}>
                      {venture.status}
                    </Badge>
                  </TableCell>
                  <TableCell>{venture.budget}</TableCell>
                  <TableCell className="text-right">{venture.progress}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}

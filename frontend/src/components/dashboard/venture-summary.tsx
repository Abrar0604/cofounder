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

const mockVentures = [
  {
    id: "v1",
    name: "Alpha Project",
    status: "Active",
    budget: "$120,000",
    progress: "65%",
  },
  {
    id: "v2",
    name: "Beta Initiative",
    status: "Pending",
    budget: "$45,000",
    progress: "10%",
  },
  {
    id: "v3",
    name: "Gamma Expansion",
    status: "Completed",
    budget: "$300,000",
    progress: "100%",
  },
]

export function VentureSummary() {
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
            {mockVentures.map((venture) => (
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
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}

"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"

interface ApprovalCardProps {
  id: string;
  title: string;
  requester: string;
  date: string;
  details: string;
}

export function ApprovalCard({ title, requester, date, details }: ApprovalCardProps) {
  const [isOpen, setIsOpen] = React.useState(false)
  const [status, setStatus] = React.useState<"Pending" | "Approved" | "Denied">("Pending")

  const handleAction = (newStatus: "Approved" | "Denied") => {
    setStatus(newStatus)
    setIsOpen(false)
  }

  return (
    <Card className="rounded-none shadow-none" data-testid="approval-card">
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-lg">{title}</CardTitle>
            <CardDescription>Requested by {requester} on {date}</CardDescription>
          </div>
          <Badge variant={status === "Pending" ? "outline" : status === "Approved" ? "default" : "secondary"}>
            {status}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-gray-600 line-clamp-2">{details}</p>
      </CardContent>
      <CardFooter className="flex justify-end gap-2">
        {status === "Pending" && (
          <Dialog open={isOpen} onOpenChange={setIsOpen}>
            <DialogTrigger render={<Button variant="outline" className="rounded-none">Review</Button>} />
            <DialogContent className="rounded-none sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>Review Approval Request</DialogTitle>
                <DialogDescription>
                  Review the details of this request before approving or denying.
                </DialogDescription>
              </DialogHeader>
              <div className="py-4">
                <h4 className="font-medium text-sm mb-2">Request Details</h4>
                <div className="bg-gray-100 p-3 text-sm text-black">
                  {details}
                </div>
              </div>
              <DialogFooter className="gap-2 sm:gap-0">
                <Button variant="outline" className="rounded-none" onClick={() => handleAction("Denied")}>Deny</Button>
                <Button className="rounded-none" onClick={() => handleAction("Approved")}>Approve</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        )}
      </CardFooter>
    </Card>
  )
}

import * as React from "react"
import { ChatWindow } from "@/components/chat/chat-window"

interface PageProps {
  params: Promise<{ startupId: string }>
}

export default async function StartupWorkspacePage({ params }: PageProps) {
  const resolvedParams = await params;
  const startupId = resolvedParams.startupId;

  return (
    <div className="flex h-full flex-col p-6">
      <div className="mb-4 flex-none">
        <h1 className="text-2xl font-bold tracking-tight">Workspace: {startupId}</h1>
        <p className="text-sm text-gray-500 mt-1">Chat with Swarn AI for this venture.</p>
      </div>
      <div className="flex-1 overflow-hidden">
        <ChatWindow startupId={startupId} />
      </div>
    </div>
  )
}

import * as React from "react"
import { ChatWindow } from "@/components/chat/chat-window"

export default function ChatPage() {
  return (
    <div className="flex h-full flex-col p-6">
      <div className="mb-4 flex-none">
        <h1 className="text-2xl font-bold tracking-tight">Chat</h1>
        <p className="text-sm text-gray-500 mt-1">Chat with Swarn AI for assistance.</p>
      </div>
      <div className="flex-1 overflow-hidden">
        <ChatWindow />
      </div>
    </div>
  )
}

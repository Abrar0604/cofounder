"use client"

import * as React from "react"
import { Message, MessageProps } from "@/components/chat/message"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { SendHorizontal } from "lucide-react"

export function ChatWindow() {
  const [messages, setMessages] = React.useState<MessageProps[]>([
    { id: "init", role: "assistant", content: "Hello, I am Swarn AI. How can I help you today?" }
  ])
  const [input, setInput] = React.useState("")
  const [isTyping, setIsTyping] = React.useState(false)
  const [clientId, setClientId] = React.useState("")
  const [isReady, setIsReady] = React.useState(false)
  const [errorMsg, setErrorMsg] = React.useState<string | null>(null)
  const scrollRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    // Generate a unique client id on mount
    const id = "client_" + Math.random().toString(36).substring(7)
    setClientId(id)
  }, [])

  React.useEffect(() => {
    if (!clientId) return;
    
    setIsReady(false)
    // Connect to SSE stream
    const eventSource = new EventSource(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/stream/${clientId}`)
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        if (data.type === "connected") {
          setIsReady(true)
        }
        else if (data.type === "agent_thought" || data.type === "agent_action") {
          setIsTyping(true)
          // Could display this somewhere, for now we just show typing indicator
        }
        else if (data.type === "agent_token") {
          setIsTyping(false)
          setMessages(prev => {
            const last = prev[prev.length - 1]
            if (last && last.role === "assistant" && last.id !== "init" && !last.isCompleted) {
              return prev.map((msg, i) => i === prev.length - 1 ? { ...msg, content: msg.content + data.payload.text } : msg)
            } else {
              // Create a new message block if none exists
              return [...prev, { id: Date.now().toString(), role: "assistant", content: data.payload.text, isCompleted: false }]
            }
          })
        }
        else if (data.type === "agent_done") {
          setIsTyping(false)
          setMessages(prev => {
            const last = prev[prev.length - 1]
            if (last && last.role === "assistant") {
              return prev.map((msg, i) => i === prev.length - 1 ? { ...msg, isCompleted: true } : msg)
            }
            return prev
          })
        }
      } catch (err) {
        console.error("SSE parse error", err)
      }
    }
    
    eventSource.onerror = () => {
      console.error("SSE connection error")
      setIsReady(false)
    }
    
    return () => {
      eventSource.close()
    }
  }, [clientId])

  const scrollToBottom = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: isTyping ? "auto" : "smooth" })
    }
  }

  React.useEffect(() => {
    scrollToBottom()
  }, [messages, isTyping])

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || !clientId || !isReady) return

    setErrorMsg(null)
    const userMessage: MessageProps = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      isCompleted: true
    }
    
    setMessages(prev => [...prev, userMessage])
    const currentInput = input
    setInput("")
    setIsTyping(true)

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/chat/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          client_id: clientId,
          message: currentInput
        })
      })
      
      if (!response.ok) {
        throw new Error(`Failed to send message: ${response.statusText}`)
      }
    } catch (error) {
      console.error("Chat send error:", error)
      setErrorMsg("Unable to send message. Please try again.")
      setIsTyping(false)
    }
  }

  return (
    <div className="flex h-full flex-col border border-gray-200 bg-white">
      <div className="border-b border-gray-200 p-4">
        <h2 className="font-semibold tracking-tight">Swarn Assistant</h2>
      </div>
      
      <ScrollArea className="flex-1 p-4">
        <div className="flex flex-col gap-2">
          {messages.map((message) => (
            <Message key={message.id} {...message} />
          ))}
          {isTyping && (
            <div className="text-sm text-gray-500 animate-pulse py-2">
              Swarn AI is thinking...
            </div>
          )}
          <div ref={scrollRef} />
        </div>
      </ScrollArea>
      
      <div className="border-t border-gray-200 p-4">
        <form onSubmit={onSubmit} className="flex gap-2">
          <Input 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={isReady ? "Type your message..." : "Connecting to Swarn..."}
            className="rounded-none border-gray-300 focus-visible:ring-0 focus-visible:border-black"
            disabled={isTyping || !isReady}
          />
          <Button 
            type="submit" 
            disabled={isTyping || !isReady || !input.trim()}
            className="rounded-none"
          >
            <SendHorizontal className="h-4 w-4 mr-2" />
            Send
          </Button>
        </form>
        {errorMsg && (
          <div className="text-sm text-red-500 mt-2">
            {errorMsg}
          </div>
        )}
      </div>
    </div>
  )
}

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
  const scrollRef = React.useRef<HTMLDivElement>(null)

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
    if (!input.trim()) return

    const userMessage: MessageProps = {
      id: Date.now().toString(),
      role: "user",
      content: input,
    }
    
    setMessages(prev => [...prev, userMessage])
    setInput("")
    setIsTyping(true)

    const assistantMessageId = (Date.now() + 1).toString()
    
    // Simulate SSE using standard fetch streams
    try {
      setMessages(prev => [...prev, { id: assistantMessageId, role: "assistant", content: "" }])
      
      const dummyResponse = "This is a simulated streaming response from the server."
      const chunks = dummyResponse.split(" ")
      
      let currentText = ""
      for (let i = 0; i < chunks.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 100))
        currentText += (i === 0 ? "" : " ") + chunks[i]
        
        setMessages(prev => prev.map(msg => 
          msg.id === assistantMessageId 
            ? { ...msg, content: currentText } 
            : msg
        ))
      }
    } catch (error) {
      console.error("Chat error:", error)
      setMessages(prev => prev.map(msg => 
        msg.id === assistantMessageId 
          ? { ...msg, content: "Sorry, an error occurred." } 
          : msg
      ))
    } finally {
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
            placeholder="Type your message..." 
            className="rounded-none border-gray-300 focus-visible:ring-0 focus-visible:border-black"
            disabled={isTyping}
          />
          <Button 
            type="submit" 
            disabled={isTyping || !input.trim()}
            className="rounded-none"
          >
            <SendHorizontal className="h-4 w-4 mr-2" />
            Send
          </Button>
        </form>
      </div>
    </div>
  )
}

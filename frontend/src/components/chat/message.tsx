import * as React from "react"
import { cn } from "@/lib/utils"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

export interface MessageProps {
  id: string;
  role: "user" | "assistant";
  content: string;
  isCompleted?: boolean;
}

export function Message({ role, content }: MessageProps) {
  const isUser = role === "user";
  
  return (
    <div className={cn("flex w-full gap-4 py-4", isUser ? "flex-row-reverse" : "flex-row")}>
      <Avatar className="h-8 w-8 rounded-none border border-black">
        {isUser ? (
          <AvatarFallback className="rounded-none bg-black text-white">U</AvatarFallback>
        ) : (
          <AvatarFallback className="rounded-none bg-white text-black">AI</AvatarFallback>
        )}
      </Avatar>
      <div className={cn("flex max-w-[80%] flex-col gap-2", isUser ? "items-end" : "items-start")}>
        <div className={cn(
          "px-4 py-2 text-sm",
          isUser ? "bg-black text-white" : "bg-gray-100 text-black border border-gray-200"
        )}>
          {content}
        </div>
      </div>
    </div>
  )
}

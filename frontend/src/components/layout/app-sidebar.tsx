import * as React from "react"
import { Home, Inbox, MessageSquare, Settings } from "lucide-react"

import { UserButton } from "@clerk/nextjs"
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarFooter,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"

import { useExperiment } from "@/components/experiments/variant-provider"
import { Badge } from "@/components/ui/badge"

const data = {
  navMain: [
    {
      title: "Venture Dashboard",
      url: "/dashboard",
      icon: Home,
    },
    {
      title: "Approvals",
      url: "/dashboard/approvals",
      icon: Inbox,
    },
    {
      title: "Chat",
      url: "/dashboard/chat",
      icon: MessageSquare,
    },
  ],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const uiExperiment = useExperiment('ui_redesign_q4')

  return (
    <Sidebar {...props}>
      <SidebarHeader>
        <div className="flex h-12 items-center px-4 font-bold tracking-tight gap-2">
          Swarn
          {uiExperiment === 'variant_a' && (
             <Badge variant="secondary" className="text-[10px] h-5">NEW</Badge>
          )}
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Application</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {data.navMain.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton render={
                    <a href={item.url}>
                      <item.icon />
                      <span>{item.title}</span>
                    </a>
                  } />
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter className="p-4 border-t border-gray-200">
        <div className="flex items-center gap-3">
          <UserButton />
          <span className="text-sm font-medium">Account</span>
        </div>
      </SidebarFooter>
    </Sidebar>
  )
}

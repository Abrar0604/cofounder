"use client";

import * as React from "react"
import { Home, Inbox, MessageSquare, Plus, CheckSquare } from "lucide-react"
import { useParams, useRouter } from "next/navigation"

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
import { Button } from "@/components/ui/button"

import { useExperiment } from "@/components/experiments/variant-provider"
import { Badge } from "@/components/ui/badge"

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const uiExperiment = useExperiment('ui_redesign_q4')
  const params = useParams()
  const router = useRouter()
  
  const startupId = params?.startupId as string | undefined

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
        {startupId ? (
          <>
            <SidebarGroup>
              <SidebarGroupLabel>Venture Workspace</SidebarGroupLabel>
              <SidebarGroupContent>
                <div className="px-4 py-2 text-sm">
                  <div className="font-semibold text-gray-900 break-words mb-2">{startupId}</div>
                  <div className="text-gray-500 text-xs">Active Approvals: 0</div>
                  <div className="text-gray-500 text-xs">Progress: In Progress</div>
                </div>
              </SidebarGroupContent>
            </SidebarGroup>
            
            <SidebarGroup>
              <SidebarGroupLabel>Actions</SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  <SidebarMenuItem>
                    <SidebarMenuButton render={
                      <a href={`/dashboard/${startupId}`}>
                        <MessageSquare />
                        <span>Workspace Chat</span>
                      </a>
                    } />
                  </SidebarMenuItem>
                  <SidebarMenuItem>
                    <SidebarMenuButton render={
                      <a href="/dashboard">
                        <Home />
                        <span>All Ventures</span>
                      </a>
                    } />
                  </SidebarMenuItem>
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </>
        ) : (
          <SidebarGroup>
            <SidebarGroupLabel>Overview</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                <SidebarMenuItem>
                  <SidebarMenuButton render={
                    <a href="/dashboard">
                      <Home />
                      <span>Venture Dashboard</span>
                    </a>
                  } />
                </SidebarMenuItem>
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        )}

        <SidebarGroup>
          <SidebarGroupLabel>Global</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton render={
                  <a href="/dashboard/approvals">
                    <Inbox />
                    <span>Global Approvals</span>
                  </a>
                } />
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton render={
                  <button onClick={() => {
                    const newId = "client_" + Math.random().toString(36).substring(7)
                    router.push(`/dashboard/${newId}`)
                  }} className="w-full text-left">
                    <Plus />
                    <span>New Startup</span>
                  </button>
                } />
              </SidebarMenuItem>
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

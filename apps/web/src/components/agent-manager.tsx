"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Plus, Users, ExternalLink } from "lucide-react"
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface Agent {
  id: string
  role: string
  status: string
  window_id: string
}

export function AgentManager({ agents }: { agents: Agent[] }) {
  const [loading, setLoading] = useState(false)

  const handleCreateAgent = async () => {
    const roles = ["Architect", "Coder", "Reviewer"]
    const role = prompt("Enter agent role (Architect/Coder/Reviewer):", roles[0])
    if (!role) return

    setLoading(true)
    try {
      const response = await fetch("http://localhost:8000/api/v1/agents/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role })
      })
      
      if (response.ok) {
        const agent = await response.json()
        const win = window.open(`/agent?agent_id=${agent.id}&role=${agent.role}`, "_blank", "width=600,height=800")
        if (!win || win.closed || typeof win.closed === 'undefined') {
          alert("Popup blocked! Please allow popups for this site to open the Agent Node window.")
        }
      }
    } catch (error) {
      console.error("Failed to create agent:", error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="bg-slate-900/40 border-slate-800 backdrop-blur-md mb-6">
      <CardHeader className="flex flex-row items-center justify-between py-4">
        <div className="flex items-center gap-2">
          <Users className="w-5 h-5 text-purple-400" />
          <CardTitle className="text-lg">Agent Registry</CardTitle>
          <CardDescription className="text-[10px] text-slate-500 uppercase tracking-wider">Deploy individual browser nodes for each agent</CardDescription>
        </div>
        <Button size="sm" onClick={handleCreateAgent} disabled={loading} className="gap-1">
          <Plus className="w-4 h-4" /> Deploy Agent
        </Button>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-3">
          {agents.length === 0 ? (
            <p className="text-sm text-slate-500 italic">No autonomous agents deployed.</p>
          ) : (
            agents.map((agent) => (
              <div 
                key={agent.id}
                className="flex items-center gap-3 bg-slate-950/50 p-2 px-3 rounded-lg border border-slate-800 hover:border-purple-500/50 transition-colors cursor-pointer group"
                onClick={() => window.open(`/agent?agent_id=${agent.id}&role=${agent.role}`, "_blank")}
              >
                <div className="flex flex-col">
                  <span className="text-xs font-bold uppercase tracking-tighter text-slate-400">{agent.role}</span>
                  <span className="text-[10px] font-mono opacity-50">{agent.id}</span>
                </div>
                <Badge variant={agent.status === "busy" ? "destructive" : "default"} className="text-[10px] py-0 h-4">
                  {agent.status}
                </Badge>
                <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  )
}

"use client"

import { useEffect, useState, useRef } from "react"
import { useSearchParams } from "next/navigation"
import { io } from "socket.io-client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Terminal, Shield, Cpu, Activity, Zap, HardDrive } from "lucide-react"

const socket = io("http://localhost:8000")

interface Log {
  agent: string
  message: string
  timestamp: number
}

export default function AgentPage() {
  const searchParams = useSearchParams()
  const agentId = searchParams.get("agent_id")
  const role = searchParams.get("role")
  
  const [logs, setLogs] = useState<Log[]>([])
  const [status, setStatus] = useState("idle")
  const [currentTask, setCurrentTask] = useState<any>(null)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!agentId) return

    socket.emit("join_agent_room", { agent_id: agentId })

    socket.on("agent_log", (log: any) => {
      if (log.agent === role || log.agent === "System") {
        setLogs(prev => [...prev, { ...log, timestamp: Date.now() }])
      }
    })

    socket.on("agent_updated", (agent: any) => {
      if (agent.id === agentId) {
        setStatus(agent.status)
      }
    })

    socket.on("task_assigned", (data: any) => {
      setCurrentTask(data.task)
      setLogs(prev => [...prev, { 
        agent: "System", 
        message: `MISSION RECEIVED: ${data.task.description}`, 
        timestamp: Date.now() 
      }])
    })

    return () => {
      socket.off("agent_log")
      socket.off("agent_updated")
      socket.off("task_assigned")
    }
  }, [agentId, role])

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [logs])

  return (
    <div className="min-h-screen bg-black text-slate-200 p-6 font-sans">
      <header className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-500/20 rounded-lg">
            <Cpu className="w-6 h-6 text-purple-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white">{role} Node</h1>
            <p className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">{agentId}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant={status === "busy" ? "destructive" : "default"} className="animate-pulse">
            {status.toUpperCase()}
          </Badge>
          <div className="flex items-center gap-1 text-[10px] font-bold text-green-500">
            <Activity className="w-3 h-3" /> LINK ACTIVE
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 gap-6">
        <Card className="bg-slate-950 border-slate-800 shadow-2xl">
          <CardHeader className="py-3 border-b border-slate-900 flex flex-row items-center justify-between">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-purple-400" />
              <CardTitle className="text-sm font-medium">Neural Execution Stream</CardTitle>
            </div>
            {currentTask && (
              <Badge variant="outline" className="text-[10px] border-purple-500/30 text-purple-400 gap-1 bg-purple-500/5">
                <Zap className="w-3 h-3" /> ACTIVE_TASK
              </Badge>
            )}
          </CardHeader>
          <CardContent className="p-0">
            {currentTask && (
              <div className="p-4 bg-purple-500/5 border-b border-slate-900">
                <div className="flex items-center gap-2 mb-1">
                  <HardDrive className="w-3 h-3 text-purple-400" />
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Current Mandate</span>
                </div>
                <div className="text-sm font-semibold text-purple-300">
                  {currentTask.description}
                </div>
                <div className="text-[10px] font-mono text-slate-600 mt-1">
                  OBJECTIVE_ID: {currentTask.id}
                </div>
              </div>
            )}
            <ScrollArea className="h-[550px] p-4" ref={scrollRef}>
              <div className="space-y-2 font-mono text-xs">
                {logs.length === 0 && (
                  <p className="text-slate-600 italic">Awaiting neural signals...</p>
                )}
                {logs.map((log, i) => (
                  <div key={i} className="flex gap-2">
                    <span className="text-slate-600">[{new Date(log.timestamp).toLocaleTimeString()}]</span>
                    <span className={log.agent === "System" ? "text-slate-500" : "text-purple-400"}>
                      {log.agent}:
                    </span>
                    <span className="text-slate-300">{log.message}</span>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      <footer className="mt-6 flex justify-center opacity-30">
        <div className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-[0.2em]">
          <Shield className="w-3 h-3 text-purple-500" /> Antigravity Swarm Peripheral
        </div>
      </footer>
    </div>
  )
}

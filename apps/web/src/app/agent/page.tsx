"use client"

import { useEffect, useState, useRef } from "react"
import { useSearchParams } from "next/navigation"
import { io } from "socket.io-client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Terminal, Shield, Cpu, Activity } from "lucide-react"

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
  const [inputMessage, setInputMessage] = useState("")
  const [isReporting, setIsReporting] = useState(false)
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
  }, [agentId, role, currentTask]) // Added currentTask to dependencies

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !agentId) return

    // Add locally for instant feedback
    const message = inputMessage.trim()
    setInputMessage("")
    
    // Emit log message to the system
    socket.emit("agent_log", { agent: role, message })
    
    // Special command: /done
    if (message.toLowerCase() === "/done" && currentTask) {
       setIsReporting(true)
       try {
         await fetch("http://localhost:8000/mcp/messages", {
           method: "POST",
           headers: { "Content-Type": "application/json" },
           body: JSON.stringify({
             jsonrpc: "2.0",
             method: "submit_task_completion",
             params: { task_id: currentTask.id, result: "Work completed via Node UI." },
             id: 1
           })
         })
         setCurrentTask(null)
       } catch (err) {
         console.error("Report failure:", err)
       } finally {
         setIsReporting(false)
       }
    }
  }

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
          <CardHeader className="py-3 border-b border-slate-900">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-purple-400" />
              <CardTitle className="text-sm font-medium">Neural Execution Stream</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <ScrollArea className="h-[500px] p-4" ref={scrollRef}>
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
            <div className="p-4 border-t border-slate-900 bg-slate-950/50">
                <div className="flex gap-2">
                    <input 
                        type="text"
                        placeholder={currentTask ? "Type message or /done to complete mandate..." : "Type message to global log..."}
                        className="flex-1 bg-black border border-slate-800 rounded px-3 py-2 text-sm focus:outline-none focus:border-purple-500 transition-colors"
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                    />
                    <Button 
                        size="sm" 
                        onClick={handleSendMessage}
                        disabled={isReporting}
                        className="bg-purple-600 hover:bg-purple-700 text-white"
                    >
                        {isReporting ? "Sync..." : "Send"}
                    </Button>
                </div>
                <div className="mt-2 text-[10px] text-slate-500 flex justify-between">
                    <span>Press Enter to broadcast</span>
                    {currentTask && <span className="text-purple-500/80 font-bold italic">Tip: Type /done to finish mission</span>}
                </div>
            </div>
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

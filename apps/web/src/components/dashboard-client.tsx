"use client"

import { useEffect, useState, useRef } from "react"
import { io } from "socket.io-client"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { motion, AnimatePresence } from "framer-motion"
import { Share2, Terminal, Activity, CheckCircle2, CircleDashed, AlertCircle, Loader2, Sparkles, Zap, ShieldCheck, ShieldAlert } from "lucide-react"
import { CommandInput } from "./command-input"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"

const socket = io("http://localhost:8000")

type TaskStatus = "pending" | "in_progress" | "done" | "error"

interface Task {
  id: string
  description: string
  role: string
  status: TaskStatus
  dependencies: string[]
  result?: string
}

interface Log {
  agent: string
  message: string
  timestamp: number
}

export default function DashboardClient() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [logs, setLogs] = useState<Log[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [autoTrigger, setAutoTrigger] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    socket.on("connect", () => setIsConnected(true))
    socket.on("disconnect", () => setIsConnected(false))
    
    socket.on("task_added", (task: Task) => setTasks(prev => {
      if (prev.find(t => t.id === task.id)) return prev
      return [...prev, task]
    }))
    
    socket.on("task_updated", (updatedTask: Task) => {
      setTasks(prev => prev.map(t => t.id === updatedTask.id ? updatedTask : t))
    })
    
    socket.on("agent_log", (log: Omit<Log, "timestamp">) => {
       setLogs(prev => [...prev, { ...log, timestamp: Date.now() }])
    })

    return () => {
      socket.off("connect")
      socket.off("disconnect")
      socket.off("task_added")
      socket.off("task_updated")
      socket.off("agent_log")
    }
  }, [])

  // Auto-scroll logs
  useEffect(() => {
    if (scrollRef.current) {
        scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [logs])

  const getStatusColor = (status: TaskStatus) => {
    switch (status) {
      case "pending": return "text-muted-foreground bg-secondary"
      case "in_progress": return "text-blue-400 bg-blue-400/10 border-blue-400/20"
      case "done": return "text-green-400 bg-green-400/10 border-green-400/20"
      case "error": return "text-red-400 bg-red-400/10 border-red-400/20"
    }
  }

  const getStatusIcon = (status: TaskStatus) => {
    switch (status) {
        case "pending": return <CircleDashed className="w-4 h-4" />
        case "in_progress": return <Loader2 className="w-4 h-4 animate-spin" />
        case "done": return <CheckCircle2 className="w-4 h-4" />
        case "error": return <AlertCircle className="w-4 h-4" />
    }
  }

  return (
    <div className="container mx-auto p-8 max-w-7xl">
      <header className="flex justify-between items-center mb-10">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Share2 className="w-8 h-8 text-primary" />
          </div>
          <div>
             <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-primary to-purple-500 bg-clip-text text-transparent">
                Antigravity Swarm
             </h1>
             <p className="text-muted-foreground">Multi-Agent Orchestration Platform</p>
          </div>
        </div>
        <div className="flex items-center gap-6">
            <div className="flex items-center space-x-2 bg-slate-900/50 p-2 px-4 rounded-full border border-slate-800">
                {autoTrigger ? <ShieldCheck className="w-4 h-4 text-green-400" /> : <ShieldAlert className="w-4 h-4 text-slate-500" />}
                <Label htmlFor="auto-trigger" className="text-xs font-bold uppercase tracking-widest cursor-pointer">
                    Auto-Trigger {autoTrigger ? "ON" : "OFF"}
                </Label>
                <Switch 
                    id="auto-trigger" 
                    checked={autoTrigger} 
                    onCheckedChange={setAutoTrigger}
                />
            </div>
            <Badge variant={isConnected ? "default" : "destructive"} className="px-4 py-1.5 text-sm uppercase tracking-wider">
                {isConnected ? "System Online" : "System Offline"}
            </Badge>
        </div>
      </header>
      
      <CommandInput />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Tasks */}
        <div className="lg:col-span-7 space-y-4">
             <div className="flex items-center gap-2 mb-2">
                <Activity className="w-5 h-5 text-primary" />
                <h2 className="text-xl font-semibold">Active Missions</h2>
             </div>
             
             <div className="grid gap-4">
                <AnimatePresence>
                    {tasks.map((task) => (
                        <motion.div
                            key={task.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            layout
                        >
                            <Card className={getStatusColor(task.status) + " border transition-all duration-300"}>
                                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                    <CardTitle className="text-base font-medium">
                                        {task.description}
                                    </CardTitle>
                                    <div className="flex items-center gap-2">
                                        {getStatusIcon(task.status)}
                                        <Badge variant="outline" className="capitalize bg-background/50 backdrop-blur-sm">
                                            {task.role}
                                        </Badge>
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-xs font-mono opacity-70">ID: {task.id}</div>
                                    {task.result && (
                                         <div className="mt-2 text-sm bg-background/50 p-2 rounded border border-border/50">
                                            {task.result}
                                         </div>
                                    )}
                                </CardContent>
                            </Card>
                        </motion.div>
                    ))}
                    {tasks.length === 0 && (
                        <div className="text-center py-20 border-2 border-dashed rounded-lg text-muted-foreground">
                            Waiting for mission instructions...
                        </div>
                    )}
                </AnimatePresence>
             </div>
        </div>

        {/* Right Column: Logs */}
        <div className="lg:col-span-5">
            <div className="flex items-center gap-2 mb-2">
                <Terminal className="w-5 h-5 text-primary" />
                <h2 className="text-xl font-semibold">Neural Link Logs</h2>
             </div>
             <Card className="bg-black/90 border-slate-800 h-[600px] flex flex-col">
                <ScrollArea className="flex-1 p-4" ref={scrollRef}>
                    <div className="space-y-3 font-mono text-sm">
                        {logs.map((log, i) => (
                            <div key={i} className="flex gap-3">
                                <span className="text-slate-500 shrink-0">
                                    {new Date(log.timestamp).toLocaleTimeString()}
                                </span>
                                <div>
                                    <span className={
                                        log.agent === "Commander" ? "text-purple-400 font-bold" :
                                        log.agent === "Orchestrator" ? "text-blue-400 font-bold" :
                                        "text-green-400 font-bold"
                                    }>
                                        [{log.agent}]
                                    </span>{" "}
                                    <span className="text-slate-300">
                                        {log.message}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </ScrollArea>
             </Card>
        </div>
      </div>
    </div>
  )
}

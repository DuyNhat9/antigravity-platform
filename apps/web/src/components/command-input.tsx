"use client"

import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Send, Zap } from "lucide-react"

export function CommandInput() {
  const [prompt, setPrompt] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSend = async () => {
    if (!prompt.trim()) return
    
    setLoading(true)
    try {
      const response = await fetch("http://localhost:8080/api/v1/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt })
      })
      if (response.ok) {
        setPrompt("")
      }
    } catch (error) {
      console.error("Failed to send command:", error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative group max-w-2xl mx-auto mb-12">
      <div className="absolute -inset-1 bg-gradient-to-r from-primary to-purple-600 rounded-lg blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"></div>
      <div className="relative flex gap-2 bg-background p-2 rounded-lg border shadow-xl">
        <div className="flex items-center px-3 text-muted-foreground">
          <Zap className="w-5 h-5 text-primary animate-pulse" />
        </div>
        <Input 
          placeholder="Transmit mission instructions to the swarm..." 
          className="border-none focus-visible:ring-0 text-lg py-6"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          disabled={loading}
        />
        <Button 
            size="lg" 
            className="px-8 shadow-lg transition-all hover:scale-105 active:scale-95"
            onClick={handleSend}
            disabled={loading}
        >
          {loading ? "Transmitting..." : <><Send className="w-4 h-4 mr-2" /> Execute</>}
        </Button>
      </div>
    </div>
  )
}

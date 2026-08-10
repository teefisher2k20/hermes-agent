import { useEffect, useState } from "react";
import { Plus, CheckCircle2, Clock, AlertCircle, Play, User, Tag } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@nous-research/ui/ui/components/button";
import { Badge } from "@nous-research/ui/ui/components/badge";
import { Input } from "@/components/ui/input";
import { usePageHeader } from "@/contexts/usePageHeader";

export interface KanbanTask {
  id: string;
  title: string;
  description: string;
  status: "todo" | "in_progress" | "in_review" | "done";
  agent: string;
  priority: "low" | "medium" | "high" | "critical";
  tags: string[];
  updatedAt: string;
}

const INITIAL_TASKS: KanbanTask[] = [
  {
    id: "task-101",
    title: "Competitor Market Scraping & Offer Deconstruction",
    description: "Deconstruct top 3 market competitors and extract pricing stack for Client A.",
    status: "done",
    agent: "CompetitorAbsorberAgent",
    priority: "high",
    tags: ["Research", "ClientA"],
    updatedAt: "2 mins ago",
  },
  {
    id: "task-102",
    title: "Lead Qualification & ICP Persona Matching",
    description: "Qualify 100 decision-maker prospects against ICP criteria.",
    status: "in_progress",
    agent: "LeadScraperAgent",
    priority: "critical",
    tags: ["Sales", "Automation"],
    updatedAt: "5 mins ago",
  },
  {
    id: "task-103",
    title: "Content Atomization & Social Post Pipeline",
    description: "Atomize weekly podcast transcript into 10 multi-platform posts.",
    status: "in_review",
    agent: "ContentAtomizerAgent",
    priority: "medium",
    tags: ["Content", "Marketing"],
    updatedAt: "12 mins ago",
  },
  {
    id: "task-104",
    title: "Roslyn Analyzer & Security Vulnerability Patch",
    description: "Run automated test suite and update vulnerable NuGet dependencies.",
    status: "todo",
    agent: "CodeQualityGuardAgent",
    priority: "high",
    tags: ["DevOps", "Security"],
    updatedAt: "20 mins ago",
  },
];

export default function KanbanPage() {
  const [tasks, setTasks] = useState<KanbanTask[]>(INITIAL_TASKS);
  const [newTitle, setNewTitle] = useState("");
  const [newAgent, setNewAgent] = useState("WorkerAgent");

  const { setTitle } = usePageHeader();
  useEffect(() => {
    setTitle?.("Multi-Agent Kanban Dispatcher");
  }, [setTitle]);

  const columns = [
    { key: "todo", title: "To Do", icon: Clock, color: "text-amber-400 border-amber-500/30" },
    { key: "in_progress", title: "In Progress", icon: Play, color: "text-blue-400 border-blue-500/30" },
    { key: "in_review", title: "In Review", icon: AlertCircle, color: "text-purple-400 border-purple-500/30" },
    { key: "done", title: "Completed", icon: CheckCircle2, color: "text-emerald-400 border-emerald-500/30" },
  ];

  const moveTask = (taskId: string, newStatus: KanbanTask["status"]) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === taskId ? { ...t, status: newStatus, updatedAt: "Just now" } : t))
    );
  };

  const addTask = () => {
    if (!newTitle.trim()) return;
    const newTask: KanbanTask = {
      id: `task-${Date.now().toString().slice(-4)}`,
      title: newTitle.trim(),
      description: "Dispatched via Hermes Kanban Dispatcher",
      status: "todo",
      agent: newAgent || "WorkerAgent",
      priority: "medium",
      tags: ["Agent", "Dispatched"],
      updatedAt: "Just now",
    };
    setTasks((prev) => [newTask, ...prev]);
    setNewTitle("");
  };

  const getPriorityBadge = (p: KanbanTask["priority"]) => {
    switch (p) {
      case "critical":
        return <Badge className="bg-red-600 text-white">Critical</Badge>;
      case "high":
        return <Badge className="bg-amber-600 text-white">High</Badge>;
      case "medium":
        return <Badge className="bg-blue-600 text-white">Medium</Badge>;
      default:
        return <Badge className="bg-slate-600 text-white">Low</Badge>;
    }
  };

  return (
    <div className="space-y-6 p-6">
      {/* Quick Dispatch Bar */}
      <Card className="bg-slate-900/60 border-slate-800">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg font-medium text-slate-100 flex items-center gap-2">
            <Plus className="w-5 h-5 text-emerald-400" /> Dispatch New Agent Task
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-3">
            <Input
              placeholder="Task Title (e.g. Run Competitor Absorber for Client B)"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              className="bg-slate-950 border-slate-800 text-slate-100"
            />
            <Input
              placeholder="Assigned Agent (e.g. GrowthAgent)"
              value={newAgent}
              onChange={(e) => setNewAgent(e.target.value)}
              className="w-64 bg-slate-950 border-slate-800 text-slate-100"
            />
            <Button onClick={addTask} className="bg-emerald-600 hover:bg-emerald-500 text-white">
              Dispatch
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Kanban Board Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {columns.map((col) => {
          const ColIcon = col.icon;
          const colTasks = tasks.filter((t) => t.status === col.key);

          return (
            <div key={col.key} className="flex flex-col gap-4">
              {/* Column Header */}
              <div className={`flex items-center justify-between p-3 rounded-lg bg-slate-900/80 border ${col.color}`}>
                <div className="flex items-center gap-2">
                  <ColIcon className={`w-4 h-4 ${col.color.split(" ")[0]}`} />
                  <span className="font-semibold text-sm text-slate-200">{col.title}</span>
                </div>
                <Badge className="bg-slate-800 text-slate-300 font-mono">{colTasks.length}</Badge>
              </div>

              {/* Task Cards */}
              <div className="space-y-3 min-h-[400px]">
                {colTasks.map((task) => (
                  <Card key={task.id} className="bg-slate-900/90 border-slate-800 hover:border-slate-700 transition">
                    <CardContent className="p-4 space-y-3">
                      <div className="flex items-start justify-between gap-2">
                        <h4 className="font-medium text-sm text-slate-100 leading-snug">{task.title}</h4>
                        {getPriorityBadge(task.priority)}
                      </div>
                      <p className="text-xs text-slate-400 line-clamp-2">{task.description}</p>

                      <div className="flex items-center gap-2 text-xs text-slate-300">
                        <User className="w-3.5 h-3.5 text-blue-400" />
                        <span className="font-mono text-blue-400">{task.agent}</span>
                      </div>

                      <div className="flex flex-wrap gap-1">
                        {task.tags.map((tag) => (
                          <span key={tag} className="text-[10px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded flex items-center gap-1">
                            <Tag className="w-2.5 h-2.5" /> {tag}
                          </span>
                        ))}
                      </div>

                      {/* Status Transition Actions */}
                      <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between">
                        <span className="text-[11px] text-slate-500">{task.updatedAt}</span>
                        <div className="flex gap-1">
                          {task.status !== "todo" && (
                            <button
                              onClick={() => moveTask(task.id, task.status === "done" ? "in_review" : task.status === "in_review" ? "in_progress" : "todo")}
                              className="text-[11px] bg-slate-800 hover:bg-slate-700 text-slate-300 px-2 py-0.5 rounded"
                            >
                              ←
                            </button>
                          )}
                          {task.status !== "done" && (
                            <button
                              onClick={() => moveTask(task.id, task.status === "todo" ? "in_progress" : task.status === "in_progress" ? "in_review" : "done")}
                              className="text-[11px] bg-slate-800 hover:bg-slate-700 text-slate-300 px-2 py-0.5 rounded"
                            >
                              →
                            </button>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

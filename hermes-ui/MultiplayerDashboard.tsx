import React, { useState } from 'react';
import { RoastRoomView } from './RoastRoomView';

export type RoomType = 'Research-Room' | 'Dev-Room' | 'Ops-Room' | 'Growth-Matrix' | 'Roast-Room';
export type MissionStatus = 'PENDING' | 'RUNNING' | 'NEEDS_REVIEW' | 'COMPLETED';

export interface Mission {
  id: string;
  title: string;
  room: RoomType;
  status: MissionStatus;
  seat: string;
  confidence: number;
}

export interface SubscriptionSeat {
  id: string;
  provider: 'CLAUDE_CODE' | 'CODEX' | 'CUSTOM_LLM';
  model: string;
  active: number;
  max: number;
  healthy: boolean;
}

export const MultiplayerDashboard: React.FC = () => {
  const [activeRoom, setActiveRoom] = useState<RoomType>('Dev-Room');
  
  const [seats] = useState<SubscriptionSeat[]>([
    { id: 'seat-claude-max-1', provider: 'CLAUDE_CODE', model: 'claude-opus-5-5', active: 2, max: 4, healthy: true },
    { id: 'seat-codex-pro-1', provider: 'CODEX', model: 'gpt-5-codex', active: 1, max: 3, healthy: true },
    { id: 'seat-local-slm-1', provider: 'CUSTOM_LLM', model: 'ollama/deepseek-r1', active: 0, max: 2, healthy: true },
  ]);

  const [missions] = useState<Mission[]>([
    { id: 'm-01', title: 'Extract AST Code Map', room: 'Research-Room', status: 'COMPLETED', seat: 'seat-claude-max-1', confidence: 0.98 },
    { id: 'm-02', title: 'Implement Multiplayer Room DAG', room: 'Dev-Room', status: 'COMPLETED', seat: 'seat-codex-pro-1', confidence: 0.95 },
    { id: 'm-03', title: 'Execute Roast Room Debate', room: 'Roast-Room', status: 'RUNNING', seat: 'seat-claude-max-1', confidence: 0.88 },
    { id: 'm-04', title: 'Production Worktree Merge', room: 'Ops-Room', status: 'NEEDS_REVIEW', seat: 'seat-claude-max-1', confidence: 0.72 },
  ]);

  const rooms: RoomType[] = ['Research-Room', 'Dev-Room', 'Ops-Room', 'Growth-Matrix', 'Roast-Room'];

  return (
    <div className="min-h-screen bg-[#0B0F17] text-white p-8 font-sans selection:bg-cyan-500/30">
      {/* Liquid-Glass Header */}
      <header className="relative mb-8 p-6 rounded-2xl bg-white/[0.03] border border-white/10 backdrop-blur-xl shadow-2xl overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 via-indigo-500/5 to-purple-500/10 pointer-events-none" />
        <div className="relative flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-white flex items-center gap-3">
              <span className="w-3 h-3 rounded-full bg-cyan-400 animate-pulse" />
              Hermes Agentic OS: Multiplayer Workspace
            </h1>
            <p className="text-sm text-gray-400 mt-1">Multi-Room Orchestrator & BYO Subscription Router</p>
          </div>
          <div className="flex gap-2">
            <span className="px-3 py-1 rounded-full text-xs font-medium bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              3 Seats Online
            </span>
            <span className="px-3 py-1 rounded-full text-xs font-medium bg-purple-500/10 text-purple-400 border border-purple-500/20">
              1 Pending Review
            </span>
          </div>
        </div>
      </header>

      {/* Main Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left Column: Room Switcher & BYO Seats */}
        <div className="space-y-6">
          {/* Room Navigation */}
          <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 backdrop-blur-md">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3 px-2">Collaborative Rooms</h2>
            <nav className="space-y-1">
              {rooms.map((room) => (
                <button
                  key={room}
                  onClick={() => setActiveRoom(room)}
                  className={`w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 flex items-center justify-between ${
                    activeRoom === room
                      ? 'bg-gradient-to-r from-cyan-500/20 to-indigo-500/20 text-cyan-300 border border-cyan-500/30'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-white/[0.02]'
                  }`}
                >
                  <span>{room}</span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-gray-400">
                    {missions.filter((m) => m.room === room).length}
                  </span>
                </button>
              ))}
            </nav>
          </div>

          {/* BYO Seat Pool Status */}
          <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 backdrop-blur-md">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3 px-2">BYO Subscription Seats</h2>
            <div className="space-y-3">
              {seats.map((seat) => (
                <div key={seat.id} className="p-3 rounded-lg bg-white/[0.02] border border-white/5">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm font-medium text-gray-200">{seat.id}</span>
                    <span className="text-xs text-cyan-400 font-mono">{seat.provider}</span>
                  </div>
                  <div className="text-xs text-gray-400 mb-2">{seat.model}</div>
                  <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden">
                    <div
                      className="bg-cyan-400 h-full rounded-full transition-all duration-300"
                      style={{ width: `${(seat.active / seat.max) * 100}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-[10px] text-gray-500 mt-1">
                    <span>Concurrency</span>
                    <span>{seat.active} / {seat.max}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Center/Right: Missions DAG & Active Room Content */}
        <div className="lg:col-span-3 space-y-6">
          {/* Active Missions DAG */}
          <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/10 backdrop-blur-md">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-lg font-semibold text-white">Active Missions: {activeRoom}</h2>
                <p className="text-xs text-gray-400 mt-0.5">Isolated Worktree Execution DAG</p>
              </div>
              <button className="px-4 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black text-xs font-semibold transition-colors shadow-lg shadow-cyan-500/20">
                + Dispatch Mission
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {missions
                .filter((m) => m.room === activeRoom)
                .map((mission) => (
                  <div
                    key={mission.id}
                    className="p-4 rounded-xl bg-white/[0.02] border border-white/10 hover:border-cyan-500/30 transition-all duration-200"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-xs font-mono text-cyan-400">{mission.id}</span>
                      <span
                        className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                          mission.status === 'COMPLETED'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : mission.status === 'RUNNING'
                            ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 animate-pulse'
                            : mission.status === 'NEEDS_REVIEW'
                            ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                            : 'bg-gray-500/10 text-gray-400'
                        }`}
                      >
                        {mission.status}
                      </span>
                    </div>
                    <h3 className="text-sm font-medium text-gray-100 mb-2">{mission.title}</h3>
                    <div className="flex justify-between items-center text-xs text-gray-400 pt-2 border-t border-white/5">
                      <span>Seat: {mission.seat}</span>
                      <span>Confidence: {(mission.confidence * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                ))}
            </div>
          </div>

          {/* Roast Room Chamber Dedicated View */}
          {activeRoom === 'Roast-Room' && (
            <div className="mt-6">
              <RoastRoomView />
            </div>
          )}

          {/* HITL Review Inbox Gate */}
          <div className="p-6 rounded-2xl bg-amber-500/[0.02] border border-amber-500/20 backdrop-blur-md">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-amber-400 mb-2">
              Human-in-the-Loop Review Gate (Active Blockers)
            </h2>
            <div className="p-4 rounded-xl bg-black/40 border border-amber-500/30 flex justify-between items-center">
              <div>
                <div className="text-sm font-medium text-gray-200">Mission m-04: Production Worktree Merge</div>
                <div className="text-xs text-gray-400 mt-1">Requires human review before advancing to main branch (Confidence: 72%).</div>
              </div>
              <div className="flex gap-2">
                <button className="px-3 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30 text-xs font-semibold">
                  Approve
                </button>
                <button className="px-3 py-1.5 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-300 border border-red-500/30 text-xs font-semibold">
                  Reject
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MultiplayerDashboard;

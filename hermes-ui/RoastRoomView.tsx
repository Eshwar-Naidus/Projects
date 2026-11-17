import React, { useState } from 'react';

export interface Advisor {
  name: string;
  framework: string;
  bias: string;
  avatarColor: string;
}

export const RoastRoomView: React.FC = () => {
  const [proposition, setProposition] = useState<string>(
    'Migrate entire monolith to 50 serverless microservices to increase team deployment velocity.'
  );

  const advisors: Advisor[] = [
    { name: 'Jeff Bezos', framework: 'Day 1 & Reversibility', bias: 'Process-as-Proxy', avatarColor: 'from-amber-600 to-amber-700' },
    { name: 'Alex Hormozi', framework: 'Grand Slam Offer', bias: 'Low Margin Complexity', avatarColor: 'from-slate-600 to-slate-700' },
    { name: 'Warren Buffett & Charlie Munger', framework: 'Moats & Inversion', bias: 'Circle of Competence', avatarColor: 'from-emerald-600 to-emerald-700' },
    { name: 'Elon Musk', framework: 'First Principles Physics', bias: 'Unquestioned Requirements', avatarColor: 'from-zinc-600 to-zinc-700' }
  ];

  return (
    <div className="p-6 rounded-2xl bg-[#090D14] text-slate-100 border border-slate-800/80 backdrop-blur-xl">
      <div className="mb-6">
        <h2 className="text-xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
          Roast Room: Elite Advisory Council Chamber
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Adversarial Multi-Round Debate & Consensus Verdict Engine
        </p>
      </div>

      {/* Proposition Box */}
      <div className="mb-6 p-4 rounded-xl bg-slate-900/50 border border-slate-800">
        <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
          Target Proposition
        </label>
        <p className="text-sm font-mono text-amber-200/90 bg-black/60 p-3 rounded-lg border border-amber-500/20">
          "{proposition}"
        </p>
      </div>

      {/* Advisory Council Chamber */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {advisors.map((adv) => (
          <div key={adv.name} className="p-4 rounded-xl bg-slate-900/30 border border-slate-800/80 hover:border-slate-700 transition-all">
            <div className={`w-8 h-8 rounded-full bg-gradient-to-tr ${adv.avatarColor} mb-3 flex items-center justify-center text-xs font-bold shadow-md text-white`}>
              {adv.name.charAt(0)}
            </div>
            <h3 className="text-sm font-semibold text-slate-200">{adv.name}</h3>
            <div className="text-xs text-amber-400/90 mt-1">{adv.framework}</div>
            <div className="text-[11px] text-slate-500 mt-2">Attacking: {adv.bias}</div>
          </div>
        ))}
      </div>

      {/* Debate Verdict Scorecard */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-amber-500/30">
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-amber-400">Consensus Verdict</span>
          <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500/10 text-amber-300 border border-amber-500/30">
            PIVOT (2 Approve, 2 Pivot)
          </span>
        </div>
        <p className="text-xs text-slate-300">
          <strong>Key Actionable Recommendation:</strong> Reversible Type 2 decision, but violates Elon Musk's 5-step algorithm: delete parts before automating. Simplify boundary before splitting into 50 services.
        </p>
      </div>
    </div>
  );
};

export default RoastRoomView;

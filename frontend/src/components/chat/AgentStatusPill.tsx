import clsx from 'clsx';
import { Loader2, Brain, Search, Wrench, PenTool, CheckCircle, AlertCircle } from 'lucide-react';
import type { AgentPhase } from '../../types';

interface AgentStatusPillProps {
  phase: AgentPhase;
  message?: string;
}

export function AgentStatusPill({ phase, message }: AgentStatusPillProps) {
  if (phase === 'idle') return null;

  const config = {
    connecting: { icon: Loader2, color: 'text-blue-400', bg: 'bg-blue-400/10', border: 'border-blue-400/20' },
    thinking: { icon: Brain, color: 'text-purple-400', bg: 'bg-purple-400/10', border: 'border-purple-400/20' },
    retrieving: { icon: Search, color: 'text-yellow-400', bg: 'bg-yellow-400/10', border: 'border-yellow-400/20' },
    using_tools: { icon: Wrench, color: 'text-orange-400', bg: 'bg-orange-400/10', border: 'border-orange-400/20' },
    synthesizing: { icon: PenTool, color: 'text-green-400', bg: 'bg-green-400/10', border: 'border-green-400/20' },
    done: { icon: CheckCircle, color: 'text-emerald-400', bg: 'bg-emerald-400/10', border: 'border-emerald-400/20' },
    error: { icon: AlertCircle, color: 'text-red-400', bg: 'bg-red-400/10', border: 'border-red-400/20' },
  }[phase] || { icon: Brain, color: 'text-gray-400', bg: 'bg-gray-400/10', border: 'border-gray-400/20' };

  const Icon = config.icon;
  const isAnimating = ['connecting', 'thinking', 'retrieving', 'using_tools', 'synthesizing'].includes(phase);

  return (
    <div className={clsx(
      "flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-medium w-fit transition-all duration-300",
      isAnimating && "anim-pulse-soft",
      config.bg, config.color, config.border
    )}
    role="status"
    aria-live="polite"
    >
      <Icon size={14} className={clsx(isAnimating && "animate-spin")} />
      <span>{message || phase}</span>
    </div>
  );
}


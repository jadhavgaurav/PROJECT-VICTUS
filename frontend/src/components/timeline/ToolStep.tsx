import clsx from 'clsx';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';
import type { ToolCall } from '../../types';

interface ToolStepProps {
  tool: ToolCall;
}

export function ToolStep({ tool }: ToolStepProps) {
  return (
    <div className="flex gap-4 anim-enter group mb-4">
      {/* Icon Column */}
      <div className="flex flex-col items-center">
        <div className={clsx(
          "w-8 h-8 rounded-full flex items-center justify-center border transition-all duration-300",
          tool.status === 'running' && "bg-blue-500/10 border-blue-500/30 text-blue-400 anim-pulse-soft",
          tool.status === 'completed' && "bg-emerald-500/10 border-emerald-500/30 text-emerald-400 transform scale-100",
          tool.status === 'failed' && "bg-red-500/10 border-red-500/30 text-red-400 anim-shake-once"
        )}>
          {tool.status === 'running' && <Loader2 size={16} className="animate-spin" />}
          {tool.status === 'completed' && <CheckCircle size={16} className="anim-scale-in" />}
          {tool.status === 'failed' && <XCircle size={16} className="anim-scale-in" />}
        </div>
        <div className="w-0.5 h-full bg-gray-800 my-2 group-last:hidden rounded-full" />
      </div>

      {/* Content Column */}
      <div className="flex-1 pb-4 min-w-0">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-semibold text-gray-200 truncate pr-2">
            {tool.name}
          </h4>
          {tool.duration ? (
            <span className="text-xs text-gray-500 font-mono animate-fade-in">
              {tool.duration}ms
            </span>
          ) : (
             <div className="h-1 w-16 bg-gray-800 rounded overflow-hidden">
                <div className="h-full w-full anim-shimmer opacity-20"></div>
             </div>
          )}
        </div>
        
        {/* Input/Output Code Blocks */}
        <div className="mt-2 text-xs font-mono origin-top animate-fade-in">
          <div className="bg-gray-900 rounded p-2 border border-gray-800/50 text-gray-400 overflow-x-auto custom-scrollbar">
            <div className="text-gray-500 mb-1 uppercase tracking-wider text-[10px]">Input</div>
            <pre>{JSON.stringify(tool.input, null, 2)}</pre>
          </div>
          
          {tool.status === 'completed' && tool.result && (
             <div className="bg-gray-900 rounded p-2 border border-emerald-900/20 text-emerald-400/80 mt-2 overflow-x-auto custom-scrollbar anim-enter" style={{ animationDelay: '100ms' }}>
               <div className="text-gray-500 mb-1 uppercase tracking-wider text-[10px]">Result</div>
               <pre className="whitespace-pre-wrap">{tool.result.length > 500 ? tool.result.slice(0, 500) + '...' : tool.result}</pre>
             </div>
          )}
          
          {tool.status === 'failed' && tool.result && (
             <div className="bg-red-900/10 rounded p-2 border border-red-900/30 text-red-400 mt-2 anim-enter" style={{ animationDelay: '100ms' }}>
                <div className="text-red-500/50 mb-1 uppercase tracking-wider text-[10px]">Error</div>
                {tool.result}
             </div>
          )}
        </div>
      </div>
    </div>
  );
}


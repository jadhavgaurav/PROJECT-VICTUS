import { useAgentStore } from '../../state/agentStore';
import { ToolStep } from './ToolStep';

export function ToolTimeline() {
  const toolCalls = useAgentStore(state => state.toolCalls);

  if (toolCalls.length === 0) return null;

  return (
    <div className="border-l border-gray-800 pl-6 ml-4 mt-6 anim-enter" role="region" aria-label="Tool execution timeline">
      <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">
        Tool Usage Timeline
      </h3>
      <div className="flex flex-col">
        {toolCalls.map((tool) => (
          <ToolStep key={tool.id} tool={tool} />
        ))}
      </div>
    </div>
  );
}

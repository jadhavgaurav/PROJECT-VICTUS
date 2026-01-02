import clsx from 'clsx';
import { Copy, RefreshCw } from 'lucide-react';
import type { ChatMessage } from '../../types';

interface MessageBubbleProps {
  message: ChatMessage;
  isStreaming?: boolean;
}

export function MessageBubble({ message, isStreaming }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={clsx(
      "flex gap-4 w-full max-w-4xl mx-auto mb-6 anim-enter",
      isUser ? "flex-row-reverse" : "flex-row"
    )}>

      {/* Avatar */}
      <div className={clsx(
        "w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold shrink-0",
        isUser 
          ? "bg-gradient-to-br from-primary-start to-primary-end text-white" 
          : "bg-white text-primary-start"
      )}>
        {isUser ? 'U' : 'V'}
      </div>

      {/* Content */}
      <div className={clsx(
        "flex flex-col max-w-[80%]",
        isUser ? "items-end" : "items-start"
      )}>
        <span className="text-xs text-gray-400 mb-1 font-medium">
          {isUser ? 'You' : 'VICTUS'}
        </span>
        
        <div className={clsx(
          "px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap shadow-sm",
          isUser 
            ? "bg-gradient-to-br from-primary-start to-primary-end text-white rounded-tr-sm" 
            : "bg-white text-gray-900 rounded-tl-sm border border-gray-200"
        )}>
          {message.content}
          
          {isUser ? null : !message.content && isStreaming && (
            <span className="inline-block w-1.5 h-4 bg-primary-start ml-1 anim-blink align-middle" />
          )}
          
          {isUser ? null : message.content && isStreaming && (
             <span className="inline-block w-1.5 h-4 bg-primary-start ml-0.5 anim-blink align-middle" />
          )}


        </div>

        {!isUser && !isStreaming && (
          <div className="flex gap-2 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <button className="p-1 hover:bg-white/10 rounded text-gray-400 hover:text-white transition-colors" title="Copy">
              <Copy size={14} />
            </button>
            <button className="p-1 hover:bg-white/10 rounded text-gray-400 hover:text-white transition-colors" title="Regenerate">
              <RefreshCw size={14} />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

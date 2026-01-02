

export function TypingIndicator() {
  return (
    <div className="flex gap-4 w-full max-w-4xl mx-auto mb-6 anim-enter">
      <div className="w-8 h-8 rounded-lg flex items-center justify-center bg-white text-primary-start text-xs font-bold shrink-0">
        V
      </div>
      
      <div className="flex flex-col items-start bg-white rounded-tr-xl rounded-br-xl rounded-bl-xl border border-gray-200 px-4 py-3">
        <span className="text-xs text-gray-400 mb-1 font-medium">VICTUS</span>
        <div className="flex gap-1 h-5 items-center">
            <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-[bounce_1.4s_infinite_ease-in-out_0s]"></div>
            <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-[bounce_1.4s_infinite_ease-in-out_0.2s]"></div>
            <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-[bounce_1.4s_infinite_ease-in-out_0.4s]"></div>
        </div>
      </div>
    </div>
  );
}

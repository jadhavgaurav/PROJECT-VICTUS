import { useState, useRef, useEffect } from 'react';
import { Send, Mic, Paperclip, X, FileText } from 'lucide-react';
import clsx from 'clsx';
import { useAgentStore } from '../../state/agentStore';

interface ComposerProps {
  onSend: (message: string, file: File | null) => void;
  disabled?: boolean;
}

export function Composer({ onSend, disabled }: ComposerProps) {
  const [input, setInput] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const phase = useAgentStore(state => state.phase);
  const isBusy = phase !== 'idle' && phase !== 'done' && phase !== 'error';

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = () => {
    if ((!input.trim() && !file) || disabled || isBusy) return;
    onSend(input, file);
    setInput('');
    setFile(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const removeFile = () => {
    setFile(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-4">
      <div className={clsx(
        "relative flex flex-col bg-gray-900 border border-gray-700 rounded-xl transition-all",
        (disabled || isBusy) && "opacity-60 cursor-not-allowed"
      )}>
        
        {/* File Preview */}
        {file && (
          <div className="px-3 pt-3 flex items-start">
            <div className="flex items-center gap-2 bg-gray-800 rounded-lg p-2 pr-3 group">
              <div className="p-2 bg-gray-700 rounded-md">
                <FileText size={16} className="text-blue-400" />
              </div>
              <div className="flex flex-col">
                <span className="text-xs font-medium text-gray-200 truncate max-w-[150px]">{file.name}</span>
                <span className="text-[10px] text-gray-400">{(file.size / 1024).toFixed(1)} KB</span>
              </div>
              <button 
                onClick={removeFile}
                className="ml-2 p-1 text-gray-400 hover:text-red-400 hover:bg-gray-700 rounded-full opacity-0 group-hover:opacity-100 transition-all"
              >
                <X size={14} />
              </button>
            </div>
          </div>
        )}

        <div className="flex items-end gap-2 p-3">
          <input 
            type="file" 
            ref={fileInputRef}
            onChange={handleFileSelect}
            className="hidden"
            accept=".pdf,.docx,.txt"
          />
          
          <button 
            onClick={() => fileInputRef.current?.click()}
            className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800 transition-colors"
            disabled={disabled || isBusy}
            title="Attach file (PDF, DOCX)"
          >
            <Paperclip size={20} />
          </button>
          
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={isBusy ? "Agent is busy..." : "Message VICTUS..."}
            className="flex-1 bg-transparent border-none focus:ring-0 outline-none focus:outline-none text-white placeholder-gray-500 resize-none max-h-[120px] py-2"
            rows={1}
            disabled={disabled || isBusy}
          />

          <div className="flex gap-1">
            {!input && !file && (
              <button 
                className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800 transition-colors"
                disabled={disabled || isBusy}
              >
                <Mic size={20} />
              </button>
            )}
            
            <button
              onClick={handleSend}
              disabled={(!input.trim() && !file) || disabled || isBusy}
              className={clsx(
                "p-2 rounded-lg transition-all duration-200",
                (input.trim() || file) && !disabled && !isBusy
                  ? "bg-primary-start text-white hover:bg-primary-end shadow-md transform hover:scale-105"
                  : "text-gray-500 bg-gray-800 cursor-not-allowed"
              )}
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

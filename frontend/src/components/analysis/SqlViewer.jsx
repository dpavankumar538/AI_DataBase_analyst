import { useState } from 'react';
import { Copy, Check, Terminal } from 'lucide-react';

export default function SqlViewer({ sqlQuery, title = 'Generated SQL Query' }) {
  const [copied, setCopied] = useState(false);

  if (!sqlQuery) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(sqlQuery);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="my-3 rounded-md border border-slate-200 bg-slate-900 text-slate-100 overflow-hidden text-xs">
      <div className="flex items-center justify-between px-3 py-2 bg-slate-950/60 border-b border-slate-800">
        <div className="flex items-center gap-2 text-slate-400">
          <Terminal className="h-3.5 w-3.5 text-blue-400" />
          <span className="font-medium text-slate-300">{title}</span>
        </div>
        <button
          type="button"
          onClick={handleCopy}
          className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-white px-2 py-0.5 rounded hover:bg-slate-800 transition-colors"
        >
          {copied ? (
            <>
              <Check className="h-3 w-3 text-emerald-400" />
              <span className="text-emerald-400">Copied</span>
            </>
          ) : (
            <>
              <Copy className="h-3 w-3" />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>
      <pre className="p-3 overflow-x-auto font-mono text-[12px] leading-relaxed text-blue-200">
        <code>{sqlQuery}</code>
      </pre>
    </div>
  );
}

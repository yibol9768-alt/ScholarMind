import { useEffect, useState } from 'react';
import { Download, ExternalLink, FileText, Maximize2, Minimize2 } from 'lucide-react';
import { useTaskStore } from '../stores/taskStore';
import * as api from '../services/api';
import type { TaskOutput } from '../shared/types';

export default function PaperPreview({ taskId }: { taskId: string }) {
  const [output, setOutput] = useState<TaskOutput | null>(null);
  const [loading, setLoading] = useState(true);
  const [fullscreen, setFullscreen] = useState(false);

  useEffect(() => {
    setLoading(true);
    api.getTaskOutput(taskId)
      .then(setOutput)
      .catch(() => setOutput(null))
      .finally(() => setLoading(false));
  }, [taskId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="w-6 h-6 border-2 border-[#10a37f] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!output?.paper_url) {
    return (
      <div className="text-center py-16">
        <FileText size={48} className="mx-auto mb-4 text-[#d9d9d9]" />
        <p className="text-sm text-[#999]">论文尚未生成</p>
        <p className="text-xs text-[#ccc] mt-1">完成 M8 论文写作模块后将在此处显示</p>
      </div>
    );
  }

  return (
    <div className={`flex flex-col ${fullscreen ? 'fixed inset-0 z-40 bg-white p-4' : ''}`}>
      {/* Toolbar */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-[#0d0d0d]">论文预览</h3>
        <div className="flex items-center gap-1">
          <a
            href={output.paper_url}
            download
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-[#666] bg-[#f4f4f4] hover:bg-[#ececec] transition-colors"
          >
            <Download size={12} />
            下载 PDF
          </a>
          <a
            href={output.paper_url}
            target="_blank"
            rel="noopener noreferrer"
            className="p-1.5 rounded-lg hover:bg-[#f4f4f4] text-[#999] transition-colors"
          >
            <ExternalLink size={14} />
          </a>
          <button
            onClick={() => setFullscreen(!fullscreen)}
            className="p-1.5 rounded-lg hover:bg-[#f4f4f4] text-[#999] transition-colors"
          >
            {fullscreen ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
          </button>
        </div>
      </div>

      {/* PDF viewer */}
      <div className={`bg-[#f4f4f4] rounded-xl overflow-hidden ${fullscreen ? 'flex-1' : 'h-[500px]'}`}>
        <iframe
          src={output.paper_url}
          className="w-full h-full border-0"
          title="Paper Preview"
        />
      </div>

      {/* Figures */}
      {output.figures && output.figures.length > 0 && (
        <div className="mt-4">
          <h4 className="text-xs font-medium text-[#999] mb-2">论文图表</h4>
          <div className="grid grid-cols-3 gap-2">
            {output.figures.map((fig, i) => (
              <div key={i} className="rounded-lg overflow-hidden border border-[#e5e5e5] bg-white">
                <img src={fig} alt={`Figure ${i + 1}`} className="w-full h-auto" />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

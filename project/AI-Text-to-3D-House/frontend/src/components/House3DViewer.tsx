import { useState } from 'react';
import type { Renders } from '../types/house';
import { API_BASE_URL } from '../services/api';

interface Props {
    renders: Renders;
}

type ViewType = 'angled' | 'front' | 'rear';

export function House3DViewer({ renders }: Props) {
    const [view, setView] = useState<ViewType>('angled');

    const imageUrl = renders[view] ? `${API_BASE_URL}${renders[view]}` : null;

    return (
        <div className="house-3d-viewer flex flex-col h-full bg-slate-900 rounded-xl overflow-hidden border border-slate-700 shadow-inner relative">
            <div className="view-selector flex gap-2 p-4 justify-center bg-slate-800/80 backdrop-blur-sm border-b border-slate-700 absolute top-0 w-full z-10">
                {(['angled', 'front', 'rear'] as ViewType[]).map(v => (
                    <button
                        key={v}
                        onClick={() => setView(v)}
                        disabled={!renders[v]}
                        className={`px-5 py-2 text-sm font-medium rounded-full capitalize transition-colors ${view === v ? 'bg-blue-600 text-white shadow-md' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'} disabled:opacity-30 disabled:cursor-not-allowed`}
                    >
                        {v} View
                    </button>
                ))}
            </div>

            <div className="image-container flex-1 flex items-center justify-center overflow-hidden bg-gradient-to-b from-slate-800 to-slate-900 pt-16">
                {imageUrl ? (
                    <img 
                        src={imageUrl} 
                        alt={`${view} view of the house`} 
                        className="max-w-full max-h-full object-contain p-2"
                    />
                ) : (
                    <div className="text-slate-500 flex flex-col items-center gap-3">
                        <svg className="w-12 h-12 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                        <span>Render not available for this view.</span>
                    </div>
                )}
            </div>
        </div>
    );
}

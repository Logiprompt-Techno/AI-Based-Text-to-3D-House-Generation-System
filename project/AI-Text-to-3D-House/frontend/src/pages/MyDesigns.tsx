import { useState, useEffect } from 'react';
import type { DesignState } from '../types/house';
import type { ViewState } from '../App';
import { getDesigns } from '../services/api';

interface Props {
    onOpenDesign: (design: DesignState) => void;
    onDeleteDesign: (id: string) => Promise<boolean>;
    onNavigate: (view: ViewState) => void;
}

export function MyDesigns({ onOpenDesign, onDeleteDesign, onNavigate }: Props) {
    const [savedDesigns, setSavedDesigns] = useState<DesignState[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchDesigns = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await getDesigns();
            // Map backend schema to frontend DesignState
            const mapped: DesignState[] = data.map((d: any) => {
                const renders = d.house3d_json?.__renders || {};
                return {
                    id: d.id,
                    name: d.name,
                    createdAt: new Date(d.created_at).getTime(),
                    updatedAt: new Date(d.updated_at).getTime(),
                    prompt: d.prompt,
                    requirements: d.requirements_json,
                    layout: d.layout_json,
                    floorplan: d.floorplan_json,
                    scene: d.house3d_json,
                    renders: renders
                };
            });
            setSavedDesigns(mapped);
        } catch (err: any) {
            console.error(err);
            setError('Failed to load your designs.');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchDesigns();
    }, []);

    const handleDelete = async (id: string) => {
        if (!window.confirm('Delete this design?')) return;
        
        const success = await onDeleteDesign(id);
        if (success) {
            setSavedDesigns(prev => prev.filter(d => d.id !== id));
        }
    };

    if (isLoading) {
        return (
            <div className="flex-1 flex items-center justify-center bg-slate-50">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex-1 flex items-center justify-center bg-slate-50 text-red-600 font-medium">
                {error}
            </div>
        );
    }

    return (
        <div className="flex-1 overflow-y-auto bg-slate-50 p-8">
            <div className="max-w-6xl mx-auto">
                <div className="flex justify-between items-end mb-8">
                    <div>
                        <h2 className="text-3xl font-bold tracking-tight text-slate-800">My Designs</h2>
                        <p className="text-slate-500 mt-2">Your saved house concepts.</p>
                    </div>
                    {savedDesigns.length > 0 && (
                        <button 
                            onClick={() => onNavigate('generator')}
                            className="px-6 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors shadow-sm focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                        >
                            Create New Design
                        </button>
                    )}
                </div>

                {savedDesigns.length === 0 ? (
                    <div className="bg-white border border-slate-200 rounded-2xl p-16 text-center shadow-sm">
                        <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-5 text-blue-600">
                            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>
                        </div>
                        <h3 className="text-xl font-semibold text-slate-800 mb-2">Your saved house designs will appear here.</h3>
                        <p className="text-slate-500 mb-8 max-w-md mx-auto">
                            Generate a new design and click save to see it in your collection.
                        </p>
                        <button 
                            onClick={() => onNavigate('generator')}
                            className="px-8 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors shadow-sm focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 inline-block"
                        >
                            Create New Design
                        </button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {savedDesigns.map(design => (
                            <div key={design.id} className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-shadow group flex flex-col">
                                {/* Thumbnail */}
                                <div className="h-48 bg-slate-100 border-b border-slate-100 relative overflow-hidden flex items-center justify-center">
                                    {design.renders?.angled ? (
                                        <img 
                                            src={design.renders.angled} 
                                            alt="House Preview" 
                                            className="w-full h-full object-cover"
                                        />
                                    ) : (
                                        <div className="text-slate-400 flex flex-col items-center">
                                            <svg className="w-10 h-10 mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"></path></svg>
                                            <span className="text-sm font-medium">No render</span>
                                        </div>
                                    )}
                                </div>
                                
                                {/* Content */}
                                <div className="p-5 flex-1 flex flex-col">
                                    <h3 className="text-slate-800 font-bold text-lg mb-1 line-clamp-1">
                                        {design.name || 'Custom House Design'}
                                    </h3>
                                    <p className="text-slate-500 text-sm line-clamp-1 mb-4 flex-1" title={design.prompt}>
                                        {design.prompt}
                                    </p>
                                    
                                    <div className="flex items-center text-xs text-slate-500 mb-5 font-medium">
                                        Updated: {new Date(design.updatedAt).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}
                                    </div>
                                    
                                    {/* Actions */}
                                    <div className="flex items-center gap-3 pt-4 border-t border-slate-100">
                                        <button 
                                            onClick={() => onOpenDesign(design)}
                                            className="flex-1 bg-slate-50 hover:bg-blue-50 text-slate-700 hover:text-blue-700 border border-slate-200 hover:border-blue-200 py-2 rounded-lg text-sm font-semibold transition-colors"
                                        >
                                            Open
                                        </button>
                                        <button 
                                            onClick={() => handleDelete(design.id)}
                                            className="px-4 py-2 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors border border-slate-200 hover:border-red-200 font-semibold text-sm bg-white"
                                        >
                                            Delete
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

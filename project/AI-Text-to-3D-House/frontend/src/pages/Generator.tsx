import { useState, useRef } from 'react';
import { HousePromptForm } from '../components/HousePromptForm';
import { FloorPlanViewer } from '../components/FloorPlanViewer';
import { House3DViewer } from '../components/House3DViewer';
import { DesignDetails } from '../components/DesignDetails';
import { SaveDesign } from '../components/SaveDesign';
import { generateHouse } from '../services/api';
import type { DesignState, RequirementOutput } from '../types/house';

interface Props {
    designState: DesignState | null;
    setDesignState: (state: DesignState | null) => void;
    onSaveDesign: (design: DesignState) => void;
}

const isHousePrompt = (text: string) => {
    const keywords = ['house', 'home', 'bhk', 'floor', 'room', 'villa', 'architecture', 'roof', 'parking', 'bedroom', 'garden'];
    return keywords.some(kw => text.toLowerCase().includes(kw));
};

const generateDesignName = (reqs: RequirementOutput) => {
    const style = reqs.house_style ? reqs.house_style.charAt(0).toUpperCase() + reqs.house_style.slice(1) : 'Custom';
    const beds = reqs.bedrooms ? `${reqs.bedrooms}BHK` : '';
    const type = reqs.house_type ? reqs.house_type.charAt(0).toUpperCase() + reqs.house_type.slice(1) : 'House';
    
    if (beds) {
        return `${style} ${beds} ${type}`.trim();
    }
    return `${style} ${type}`.trim();
};

export function Generator({ designState, setDesignState, onSaveDesign }: Props) {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState<'2d' | '3d' | 'details'>('3d');
    const generationIdRef = useRef<string>('');

    const handleGenerate = async (prompt: string) => {
        if (!isHousePrompt(prompt)) {
            setError('This AI is designed for house planning. Please describe the house you want to create.');
            return;
        }

        const genId = crypto.randomUUID();
        generationIdRef.current = genId;
        
        setIsLoading(true);
        setError(null);
        setDesignState(null); // Clear active design immediately to prevent stale output
        
        try {
            const data = await generateHouse(prompt);
            
            // Race condition guard
            if (generationIdRef.current !== genId) {
                return;
            }

            const name = generateDesignName(data.requirements);

            setDesignState({
                id: crypto.randomUUID(),
                name,
                createdAt: Date.now(),
                updatedAt: Date.now(),
                prompt,
                requirements: data.requirements,
                layout: data.layout,
                floorplan: data.floorplan,
                scene: data.scene,
                renders: data.renders
            });
            setActiveTab('3d');
        } catch (err: any) {
            // Race condition guard for errors
            if (generationIdRef.current !== genId) {
                return;
            }
            setError(err.message || 'An unexpected error occurred during generation. Please try again.');
        } finally {
            if (generationIdRef.current === genId) {
                setIsLoading(false);
            }
        }
    };

    return (
        <div className="flex-1 flex overflow-hidden">
            {/* Left Panel: Input & Actions */}
            <div className="w-1/3 min-w-[400px] max-w-[500px] border-r border-slate-200 bg-white flex flex-col z-0 shadow-sm overflow-y-auto">
                <div className="p-8 flex flex-col h-full">
                    <div className="mb-8">
                        <h2 className="text-2xl font-bold text-slate-800 mb-2">Start with an idea for your house</h2>
                        <p className="text-sm text-slate-500">
                            Describe the home you want to create.
                        </p>
                    </div>

                    <HousePromptForm 
                        onSubmit={handleGenerate} 
                        isLoading={isLoading} 
                        initialPrompt={designState?.prompt} 
                    />
                    
                    {error && (
                        <div className="mt-6 p-4 bg-red-50 text-red-700 border border-red-200 rounded-lg text-sm shadow-sm">
                            <strong className="font-semibold block mb-1">Generation failed</strong>
                            {error}
                            <button 
                                onClick={() => setError(null)}
                                className="mt-3 text-red-700 hover:text-red-800 underline font-medium"
                            >
                                Dismiss
                            </button>
                        </div>
                    )}

                    <div className="flex-1"></div>
                    
                    {designState && !isLoading && (
                        <div className="mt-8 pt-8 border-t border-slate-100">
                            <SaveDesign onSave={() => onSaveDesign(designState)} />
                        </div>
                    )}
                </div>
            </div>
            
            {/* Right Panel: Results Viewer */}
            <div className="flex-1 bg-slate-50 relative flex flex-col overflow-hidden">
                {!designState && !isLoading ? (
                    <div className="flex-1 flex items-center justify-center text-slate-400">
                        <div className="text-center">
                            <svg className="w-16 h-16 mx-auto mb-4 opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
                            <p className="text-lg font-medium">Your design will appear here</p>
                        </div>
                    </div>
                ) : isLoading ? (
                    <div className="flex-1 flex flex-col items-center justify-center">
                        <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-6"></div>
                        <h3 className="text-xl font-semibold text-slate-800 mb-2">Creating your house design...</h3>
                        <div className="text-slate-500 text-sm space-y-1 text-center">
                            <p className="animate-pulse">Parsing architectural requirements...</p>
                        </div>
                    </div>
                ) : (
                    <div className="flex-1 flex flex-col p-6 h-full overflow-hidden">
                        {/* Tabs */}
                        <div className="flex space-x-2 mb-6 bg-white p-1.5 rounded-lg shadow-sm border border-slate-200 self-start">
                            <button
                                onClick={() => setActiveTab('3d')}
                                className={`px-5 py-2 rounded-md text-sm font-medium transition-colors ${
                                    activeTab === '3d' 
                                    ? 'bg-blue-50 text-blue-700 shadow-sm' 
                                    : 'text-slate-600 hover:text-slate-800 hover:bg-slate-50'
                                }`}
                            >
                                3D House
                            </button>
                            <button
                                onClick={() => setActiveTab('2d')}
                                className={`px-5 py-2 rounded-md text-sm font-medium transition-colors ${
                                    activeTab === '2d' 
                                    ? 'bg-blue-50 text-blue-700 shadow-sm' 
                                    : 'text-slate-600 hover:text-slate-800 hover:bg-slate-50'
                                }`}
                            >
                                2D Floor Plan
                            </button>
                            <button
                                onClick={() => setActiveTab('details')}
                                className={`px-5 py-2 rounded-md text-sm font-medium transition-colors ${
                                    activeTab === 'details' 
                                    ? 'bg-blue-50 text-blue-700 shadow-sm' 
                                    : 'text-slate-600 hover:text-slate-800 hover:bg-slate-50'
                                }`}
                            >
                                Design Details
                            </button>
                        </div>

                        {/* Content Area */}
                        <div className="flex-1 relative bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden max-h-[65vh]">
                            {activeTab === '3d' && designState?.renders && (
                                <House3DViewer renders={designState.renders} />
                            )}
                            {activeTab === '2d' && designState?.floorplan && (
                                <div className="absolute inset-0 overflow-auto bg-slate-50/50">
                                    <FloorPlanViewer floorplan={designState.floorplan} />
                                </div>
                            )}
                            {activeTab === 'details' && designState?.requirements && (
                                <div className="absolute inset-0 overflow-auto bg-white p-6">
                                    <DesignDetails requirements={designState.requirements} />
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

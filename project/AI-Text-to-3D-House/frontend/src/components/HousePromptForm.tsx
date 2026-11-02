import { useState, useEffect } from 'react';

interface Props {
    onSubmit: (prompt: string) => void;
    isLoading: boolean;
    initialPrompt?: string;
}

export function HousePromptForm({ onSubmit, isLoading, initialPrompt }: Props) {
    const [prompt, setPrompt] = useState(initialPrompt || '');

    useEffect(() => {
        if (initialPrompt !== undefined) {
            setPrompt(initialPrompt);
        } else {
            setPrompt('');
        }
    }, [initialPrompt]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (prompt.trim()) {
            onSubmit(prompt);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="w-full bg-white">
            <div className="relative">
                <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    disabled={isLoading}
                    placeholder="Describe your dream house..."
                    rows={6}
                    className="w-full p-4 border border-slate-300 rounded-lg resize-none mb-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow bg-slate-50/50 text-slate-800 text-lg placeholder-slate-400"
                />
            </div>
            
            <div className="mb-6">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 block">Example prompts:</span>
                <ul className="text-sm text-slate-600 space-y-1.5 pl-1">
                    <li className="flex items-start gap-2">
                        <span className="text-slate-300">•</span>
                        Modern Kerala 4BHK with balcony
                    </li>
                    <li className="flex items-start gap-2">
                        <span className="text-slate-300">•</span>
                        Minimal 2BHK flat roof house with garden
                    </li>
                    <li className="flex items-start gap-2">
                        <span className="text-slate-300">•</span>
                        Traditional 3BHK with car parking
                    </li>
                </ul>
            </div>
            <button 
                type="submit" 
                disabled={isLoading || !prompt.trim()}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-lg shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2 text-base"
            >
                {isLoading ? (
                    <>
                        <svg className="animate-spin -ml-1 mr-3 h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                        Generating...
                    </>
                ) : 'Generate House'}
            </button>
        </form>
    );
}

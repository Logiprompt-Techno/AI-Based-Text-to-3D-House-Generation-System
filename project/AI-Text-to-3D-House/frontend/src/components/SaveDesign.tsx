import { useState } from 'react';

interface Props {
    onSave: () => void;
}

export function SaveDesign({ onSave }: Props) {
    const [saved, setSaved] = useState(false);

    const handleSave = () => {
        onSave();
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
    };

    return (
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
            <div>
                <h3 className="text-lg font-semibold text-slate-800">Save Your Design</h3>
                <p className="text-sm text-slate-500 mt-1">
                    {saved ? <span className="text-green-600 font-medium">Design saved successfully.</span> : 'Store this design layout and architectural renders.'}
                </p>
            </div>
            <button
                onClick={handleSave}
                disabled={saved}
                className={`px-6 py-2.5 rounded-lg font-medium shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
                    saved 
                    ? 'bg-green-100 text-green-700 border border-green-200' 
                    : 'bg-slate-800 text-white hover:bg-slate-700'
                }`}
            >
                {saved ? 'Saved!' : 'Save Design'}
            </button>
        </div>
    );
}

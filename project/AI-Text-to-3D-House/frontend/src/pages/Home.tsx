import type { ViewState } from '../App';

interface Props {
    onNavigate: (view: ViewState) => void;
}

export function Home({ onNavigate }: Props) {
    return (
        <div className="flex-1 flex flex-col items-center justify-center p-8 overflow-y-auto">
            {/* Hero */}
            <div className="max-w-3xl w-full text-center mb-16">
                <p className="text-sm font-bold text-blue-600 tracking-widest uppercase mb-4">
                    AI-Powered Architectural Design
                </p>
                <h2 className="text-5xl font-extrabold tracking-tight text-slate-900 mb-6 leading-tight">
                    Turn your idea <br className="hidden sm:block" /> into a house.
                </h2>
                <p className="text-lg text-slate-500 mb-10 max-w-2xl mx-auto">
                    Describe your home requirements and generate a coordinated 2D floor plan and 3D architectural view in seconds.
                </p>
                <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                    <button 
                        onClick={() => onNavigate('generator')}
                        className="px-8 py-3.5 bg-blue-600 text-white rounded-lg font-medium shadow-sm hover:bg-blue-700 transition-all focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 text-lg w-full sm:w-auto"
                    >
                        Create New Design
                    </button>
                    <button 
                        onClick={() => onNavigate('my-designs')}
                        className="px-8 py-3.5 bg-white border border-slate-300 text-slate-700 rounded-lg font-medium shadow-sm hover:bg-slate-50 transition-all focus:ring-2 focus:ring-offset-2 focus:ring-slate-500 text-lg w-full sm:w-auto"
                    >
                        View My Designs
                    </button>
                </div>
            </div>

            {/* Feature Cards */}
            <div className="max-w-5xl w-full grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
                {/* Card 1 */}
                <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm flex flex-col items-center text-center hover:shadow-md transition-shadow">
                    <div className="w-12 h-12 bg-slate-50 rounded-full flex items-center justify-center mb-4 text-blue-600">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z"></path></svg>
                    </div>
                    <h3 className="text-lg font-semibold text-slate-800 mb-2">2D Floor Plan</h3>
                    <p className="text-slate-500 text-sm">Generate a coordinated architectural floor plan.</p>
                </div>

                {/* Card 2 */}
                <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm flex flex-col items-center text-center hover:shadow-md transition-shadow">
                    <div className="w-12 h-12 bg-slate-50 rounded-full flex items-center justify-center mb-4 text-blue-600">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg>
                    </div>
                    <h3 className="text-lg font-semibold text-slate-800 mb-2">3D House</h3>
                    <p className="text-slate-500 text-sm">Preview your design from multiple views.</p>
                </div>

                {/* Card 3 */}
                <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm flex flex-col items-center text-center hover:shadow-md transition-shadow">
                    <div className="w-12 h-12 bg-slate-50 rounded-full flex items-center justify-center mb-4 text-blue-600">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"></path></svg>
                    </div>
                    <h3 className="text-lg font-semibold text-slate-800 mb-2">Save Designs</h3>
                    <p className="text-slate-500 text-sm">Save concepts and revisit them later.</p>
                </div>
            </div>
        </div>
    );
}

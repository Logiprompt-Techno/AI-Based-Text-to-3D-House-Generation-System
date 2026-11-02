import type { RequirementOutput } from '../types/house';

interface Props {
    requirements: RequirementOutput;
}

export function DesignDetails({ requirements }: Props) {
    const { 
        house_style, house_type, roof_type, floors, bedrooms, bathrooms, 
        parking_spaces, balconies, terraces, plot_width, plot_depth, special_requirements, source_text
    } = requirements;

    const renderField = (label: string, value: string | number | undefined | null, capitalize = false) => {
        const hasValue = value !== undefined && value !== null && value !== '';
        return (
            <div className="flex justify-between items-center py-3 border-b border-slate-100 last:border-0">
                <span className="text-sm font-medium text-slate-500">{label}</span>
                <span className={`text-sm font-medium ${hasValue ? 'text-slate-800' : 'text-slate-400 italic'} ${capitalize && hasValue ? 'capitalize' : ''}`}>
                    {hasValue ? value : 'Not specified'}
                </span>
            </div>
        );
    };

    return (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm h-full flex flex-col">
            <div className="p-5 border-b border-slate-100 bg-slate-50">
                <h2 className="text-lg font-semibold text-slate-800">Architectural Specifications</h2>
                <p className="text-sm text-slate-500">Parsed generation properties</p>
            </div>
            
            <div className="p-6 overflow-y-auto flex-1 space-y-8">
                {source_text && (
                    <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg">
                        <span className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Original Prompt</span>
                        <span className="text-slate-800 font-medium italic">"{source_text}"</span>
                    </div>
                )}
            
                <div>
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">House</h3>
                    <div className="bg-white border border-slate-200 rounded-lg px-4">
                        {renderField('Architecture Style', house_style, true)}
                        {renderField('House Type', house_type, true)}
                        {renderField('Roof Type', roof_type, true)}
                        {renderField('Floors', floors)}
                        {renderField('Bedrooms', bedrooms)}
                        {renderField('Bathrooms', bathrooms)}
                    </div>
                </div>

                <div>
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Site</h3>
                    <div className="bg-white border border-slate-200 rounded-lg px-4">
                        {renderField('Plot Width', plot_width ? `${plot_width}m` : undefined)}
                        {renderField('Plot Depth', plot_depth ? `${plot_depth}m` : undefined)}
                    </div>
                </div>

                <div>
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Features</h3>
                    <div className="bg-white border border-slate-200 rounded-lg px-4">
                        {renderField('Parking Spaces', parking_spaces)}
                        {renderField('Balconies', balconies)}
                        {renderField('Terraces', terraces)}
                    </div>
                </div>
                
                <div className="pt-2">
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Special Requirements</h3>
                    {special_requirements && special_requirements.length > 0 ? (
                        <ul className="list-disc pl-5 space-y-1.5 text-slate-800 text-sm font-medium">
                            {special_requirements.map((req, i) => (
                                <li key={i}>{req}</li>
                            ))}
                        </ul>
                    ) : (
                        <p className="text-sm font-medium text-slate-400 italic">Not specified</p>
                    )}
                </div>
            </div>
        </div>
    );
}

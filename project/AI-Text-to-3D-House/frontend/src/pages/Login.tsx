import { useState } from 'react';
import { loginUser, registerUser } from '../services/api';

interface Props {
    onLogin: (token: string, user: any) => void;
}

export function Login({ onLogin }: Props) {
    const [isRegistering, setIsRegistering] = useState(false);
    
    // Form fields
    const [fullName, setFullName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [repeatPassword, setRepeatPassword] = useState('');
    
    // UX state
    const [showPassword, setShowPassword] = useState(false);
    
    // Error state (inline per field)
    const [errors, setErrors] = useState<Record<string, string>>({});
    const [globalError, setGlobalError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const validateForm = () => {
        const newErrors: Record<string, string> = {};
        
        // Email validation
        if (!email.trim()) {
            newErrors.email = 'Email is required';
        } else if (!/^\S+@\S+\.\S+$/.test(email)) {
            newErrors.email = 'Enter a valid email address';
        }
        
        // Password validation
        if (!password) {
            newErrors.password = 'Password is required';
        } else if (isRegistering) {
            if (password.length < 8) {
                newErrors.password = 'Password must be at least 8 characters';
            } else if (!/[A-Za-z]/.test(password)) {
                newErrors.password = 'Password must contain at least one letter';
            } else if (!/[0-9]/.test(password)) {
                newErrors.password = 'Password must contain at least one number';
            }
        }

        // Register specific validation
        if (isRegistering) {
            if (!fullName.trim()) {
                newErrors.fullName = 'Full Name is required';
            } else if (fullName.trim().length < 2) {
                newErrors.fullName = 'Full Name must be at least 2 characters';
            }

            if (!repeatPassword) {
                newErrors.repeatPassword = 'Please repeat your password';
            } else if (password !== repeatPassword) {
                newErrors.repeatPassword = 'Passwords do not match';
            }
        }
        
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setGlobalError(null);
        
        if (!validateForm()) {
            return;
        }

        setLoading(true);
        try {
            if (isRegistering) {
                // Backend API doesn't store full name currently, so we pass what it accepts
                const user = await registerUser(email, password);
                const loginRes = await loginUser(email, password);
                onLogin(loginRes.access_token, user);
            } else {
                const loginRes = await loginUser(email, password);
                onLogin(loginRes.access_token, null);
            }
        } catch (err: any) {
            console.error(err);
            if (err.message.includes('400')) {
                setGlobalError('Email already registered. Try logging in.');
            } else if (err.message.includes('401')) {
                setGlobalError('Incorrect email or password.');
            } else {
                setGlobalError('Authentication failed. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    const toggleMode = () => {
        setIsRegistering(!isRegistering);
        setErrors({});
        setGlobalError(null);
        setPassword('');
        setRepeatPassword('');
    };

    return (
        <div className="min-h-screen w-full flex flex-col items-center justify-center relative font-sans text-slate-800 bg-[#f9fafb] overflow-hidden">
            
            {/* Subtle Architectural Grid */}
            <div className="absolute inset-0 pointer-events-none opacity-[0.03]" 
                 style={{ backgroundImage: 'linear-gradient(#000 1px, transparent 1px), linear-gradient(90deg, #000 1px, transparent 1px)', backgroundSize: '40px 40px', backgroundPosition: 'center center' }}>
            </div>
            
            {/* Background Line-Art House Composition */}
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-[0.05] overflow-hidden">
                <svg className="w-full h-full max-w-[1200px] text-orange-900" viewBox="0 0 1200 800" fill="none" stroke="currentColor" strokeWidth="1.5">
                    {/* Abstract Floorplan / House lines */}
                    <path d="M 300 500 L 900 500 L 900 300 L 300 300 Z" />
                    <path d="M 300 300 L 600 150 L 900 300" />
                    <path d="M 600 150 L 600 500" strokeDasharray="4 4" />
                    <rect x="400" y="300" width="150" height="200" />
                    <rect x="650" y="350" width="100" height="150" />
                    <circle cx="600" cy="150" r="4" fill="currentColor" />
                </svg>
            </div>

            <div className="z-10 w-full px-6 sm:px-0 flex flex-col items-center">
                
                {/* Branding Block */}
                <div className="text-center mb-8 w-full">
                    <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-slate-900 mb-2 whitespace-normal sm:whitespace-nowrap flex items-center justify-center gap-2">
                        <svg className="w-8 h-8 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                        </svg>
                        AI Text-to-3D House
                    </h1>
                    <p className="text-slate-500 text-sm font-medium">
                        Architectural design powered by AI.
                    </p>
                </div>

                {/* Main Card */}
                <div className="w-full max-w-[440px] bg-white p-8 sm:p-10 rounded-2xl border border-slate-200 shadow-xl shadow-slate-200/50 relative">
                    
                    {/* Top warm accent line */}
                    <div className="absolute top-0 left-0 right-0 h-1 bg-orange-500 rounded-t-2xl"></div>
                    
                    <div className="mb-6">
                        <h2 className="text-2xl font-bold text-slate-800">
                            {isRegistering ? 'Create an Account' : 'Welcome Back'}
                        </h2>
                        <p className="text-slate-500 text-sm mt-1">
                            {isRegistering ? 'Register to start creating floor plans.' : 'Sign in to access your designs.'}
                        </p>
                    </div>
                    
                    <form onSubmit={handleSubmit} className="space-y-4" noValidate>
                        
                        {isRegistering && (
                            <div>
                                <label className="block text-sm font-semibold text-slate-700 mb-1">Full Name</label>
                                <input 
                                    type="text"
                                    value={fullName}
                                    onChange={(e) => setFullName(e.target.value)}
                                    className={`w-full px-4 py-2.5 bg-slate-50 border ${errors.fullName ? 'border-red-400 focus:ring-red-100' : 'border-slate-200 focus:ring-orange-100 focus:border-orange-400'} rounded-lg focus:bg-white focus:ring-2 outline-none transition-all text-sm text-slate-800 placeholder-slate-400`}
                                    placeholder="John Doe"
                                    disabled={loading}
                                />
                                {errors.fullName && <p className="text-red-500 text-xs mt-1 font-medium">{errors.fullName}</p>}
                            </div>
                        )}

                        <div>
                            <label className="block text-sm font-semibold text-slate-700 mb-1">Email address</label>
                            <input 
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className={`w-full px-4 py-2.5 bg-slate-50 border ${errors.email ? 'border-red-400 focus:ring-red-100' : 'border-slate-200 focus:ring-orange-100 focus:border-orange-400'} rounded-lg focus:bg-white focus:ring-2 outline-none transition-all text-sm text-slate-800 placeholder-slate-400`}
                                placeholder="name@example.com"
                                disabled={loading}
                            />
                            {errors.email && <p className="text-red-500 text-xs mt-1 font-medium">{errors.email}</p>}
                        </div>

                        <div>
                            <label className="block text-sm font-semibold text-slate-700 mb-1">Password</label>
                            <div className="relative">
                                <input 
                                    type={showPassword ? "text" : "password"}
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className={`w-full px-4 py-2.5 bg-slate-50 border ${errors.password ? 'border-red-400 focus:ring-red-100' : 'border-slate-200 focus:ring-orange-100 focus:border-orange-400'} rounded-lg focus:bg-white focus:ring-2 outline-none transition-all text-sm text-slate-800 placeholder-slate-400 pr-12`}
                                    placeholder="••••••••"
                                    disabled={loading}
                                />
                                <button 
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 focus:outline-none text-xs font-semibold"
                                >
                                    {showPassword ? 'HIDE' : 'SHOW'}
                                </button>
                            </div>
                            {errors.password && <p className="text-red-500 text-xs mt-1 font-medium">{errors.password}</p>}
                        </div>

                        {isRegistering && (
                            <div>
                                <label className="block text-sm font-semibold text-slate-700 mb-1">Repeat Password</label>
                                <div className="relative">
                                    <input 
                                        type={showPassword ? "text" : "password"}
                                        value={repeatPassword}
                                        onChange={(e) => setRepeatPassword(e.target.value)}
                                        className={`w-full px-4 py-2.5 bg-slate-50 border ${errors.repeatPassword ? 'border-red-400 focus:ring-red-100' : 'border-slate-200 focus:ring-orange-100 focus:border-orange-400'} rounded-lg focus:bg-white focus:ring-2 outline-none transition-all text-sm text-slate-800 placeholder-slate-400 pr-12`}
                                        placeholder="••••••••"
                                        disabled={loading}
                                    />
                                </div>
                                {errors.repeatPassword && <p className="text-red-500 text-xs mt-1 font-medium">{errors.repeatPassword}</p>}
                            </div>
                        )}

                        {globalError && (
                            <div className="text-red-600 text-sm font-medium p-3 rounded bg-red-50 border border-red-100">
                                {globalError}
                            </div>
                        )}

                        <button 
                            type="submit"
                            disabled={loading}
                            className="w-full mt-4 bg-orange-600 hover:bg-orange-700 disabled:bg-orange-400 text-white font-semibold text-sm py-3 rounded-lg transition-all focus:outline-none focus:ring-4 focus:ring-orange-100 shadow-md"
                        >
                            {loading ? 'Please wait...' : (isRegistering ? 'Create Account' : 'Sign In')}
                        </button>
                    </form>
                </div>

                <div className="mt-6 text-center text-sm text-slate-500">
                    {isRegistering ? 'Already have an account?' : 'New here?'}
                    <button 
                        onClick={toggleMode}
                        className="ml-1.5 text-orange-600 hover:text-orange-700 font-semibold transition-colors focus:outline-none"
                    >
                        {isRegistering ? 'Sign In' : 'Create an account'}
                    </button>
                </div>
            </div>
        </div>
    );
}

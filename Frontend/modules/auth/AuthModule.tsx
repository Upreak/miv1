import React, { useState } from 'react';
import { UserRole, User } from '../../types';
import { ShieldCheck, Users, Briefcase, UserCircle, User as UserIcon, ArrowLeft, Phone, KeyRound, ArrowRight } from 'lucide-react';
import { useToast } from '../ui/ToastContext';

interface AuthProps {
  onLogin: (user: User) => void;
  onBack: () => void;
}

export const AuthModule: React.FC<AuthProps> = ({ onLogin, onBack }) => {
  const [selectedRole, setSelectedRole] = useState<UserRole | null>(null);
  const [phoneNumber, setPhoneNumber] = useState('');
  const [otp, setOtp] = useState('');
  const [step, setStep] = useState<'PHONE' | 'OTP'>('PHONE');
  const [isLoading, setIsLoading] = useState(false);
  const { addToast } = useToast();

  const handleSendOtp = (e: React.FormEvent) => {
    e.preventDefault();
    if (!phoneNumber || phoneNumber.length < 10) {
      addToast('Please enter a valid phone number', 'error');
      return;
    }

    setIsLoading(true);
    // Simulate sending OTP
    setTimeout(() => {
      setIsLoading(false);
      setStep('OTP');
      addToast('OTP Sent: 1234', 'info'); // exposing OTP for demo purposes
    }, 1000);
  };

  const handleVerifyOtp = (e: React.FormEvent) => {
    e.preventDefault();
    if (otp !== '1234') { // Mock OTP validation
      addToast('Invalid OTP. Please try again.', 'error');
      return;
    }

    setIsLoading(true);

    // Simulate API Verification and Login
    setTimeout(() => {
      const mockUser: User = {
        id: `user-${Math.random().toString(36).substr(2, 9)}`,
        name: selectedRole === UserRole.ADMIN ? 'Admin User' : 
              selectedRole === UserRole.SALES ? 'Sales Rep' : 
              selectedRole === UserRole.RECRUITER ? 'Recruiter Jane' : 'Candidate One',
        email: `${phoneNumber}@sree.ai`, // Generated placeholder email for system compatibility
        role: selectedRole!,
        avatar: `https://picsum.photos/seed/${selectedRole}${phoneNumber}/200`,
        status: 'Active'
      };
      setIsLoading(false);
      addToast(`Welcome back, ${mockUser.name}!`, 'success');
      onLogin(mockUser);
    }, 1000);
  };

  const resetFlow = () => {
    setSelectedRole(null);
    setStep('PHONE');
    setPhoneNumber('');
    setOtp('');
  };

  const renderRoleSelection = () => (
    <div className="space-y-4 animate-in fade-in slide-in-from-right-8">
      <button onClick={() => onBack()} className="text-slate-400 hover:text-slate-600 flex items-center gap-2 text-sm font-bold mb-6">
        <ArrowLeft size={16} /> Back to Home
      </button>

      <h2 className="text-2xl font-bold text-slate-800 mb-6">Select Portal</h2>
      
      <div className="space-y-4">
        <button onClick={() => setSelectedRole(UserRole.CANDIDATE)} className="w-full p-4 bg-white border hover:border-blue-500 rounded-xl flex items-center gap-4 transition-all group shadow-sm hover:shadow-md">
          <div className="p-2 bg-yellow-100 text-yellow-600 rounded-lg group-hover:bg-yellow-600 group-hover:text-white transition-colors">
            <UserIcon size={20} />
          </div>
          <div className="text-left">
            <div className="font-semibold text-slate-900">Candidate Portal</div>
            <div className="text-xs text-slate-500">Job Search & Applications</div>
          </div>
        </button>

        <div className="border-t pt-4 mt-2">
          <p className="text-xs font-bold text-slate-400 uppercase mb-3">Internal Teams</p>
          <div className="space-y-3">
            <button onClick={() => setSelectedRole(UserRole.SALES)} className="w-full p-3 bg-slate-50 border hover:border-blue-500 rounded-lg flex items-center gap-3 transition-all hover:bg-white">
              <div className="p-1.5 bg-purple-100 text-purple-600 rounded">
                <Briefcase size={16} />
              </div>
              <div className="text-left">
                 <div className="text-sm font-semibold text-slate-700">Sales Team</div>
                 <div className="text-[10px] text-slate-400">CRM & Client Mgmt</div>
              </div>
            </button>

            <button onClick={() => setSelectedRole(UserRole.RECRUITER)} className="w-full p-3 bg-slate-50 border hover:border-blue-500 rounded-lg flex items-center gap-3 transition-all hover:bg-white">
              <div className="p-1.5 bg-blue-100 text-blue-600 rounded">
                <UserCircle size={16} />
              </div>
              <div className="text-left">
                 <div className="text-sm font-semibold text-slate-700">Recruiter</div>
                 <div className="text-[10px] text-slate-400">Sourcing & Screening</div>
              </div>
            </button>
            
            <button onClick={() => setSelectedRole(UserRole.ADMIN)} className="w-full p-3 bg-slate-50 border hover:border-blue-500 rounded-lg flex items-center gap-3 transition-all hover:bg-white">
              <div className="p-1.5 bg-red-100 text-red-600 rounded">
                <ShieldCheck size={16} />
              </div>
              <div className="text-sm font-semibold text-slate-700">Admin Console</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderPhoneLogin = () => {
    const roleName = selectedRole === UserRole.SALES ? 'Sales' : selectedRole === UserRole.RECRUITER ? 'Recruiter' : selectedRole === UserRole.ADMIN ? 'Admin' : 'Candidate';

    return (
      <div className="animate-in fade-in slide-in-from-right-8 max-w-md mx-auto w-full">
         <button onClick={resetFlow} className="text-slate-400 hover:text-slate-600 flex items-center gap-2 text-sm font-bold mb-6">
           <ArrowLeft size={16} /> Back to Roles
         </button>

         <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-slate-900">Welcome Back</h2>
            <p className="text-slate-500 text-sm mt-1">
               Login to your {roleName} account using your mobile number.
            </p>
         </div>

         {step === 'PHONE' ? (
           <form onSubmit={handleSendOtp} className="space-y-6">
              <div>
                 <label className="block text-sm font-bold text-slate-700 mb-1">Mobile Number</label>
                 <div className="relative">
                    <Phone className="absolute left-3 top-3 text-slate-400" size={18} />
                    <input 
                      type="tel" 
                      required 
                      value={phoneNumber}
                      onChange={e => setPhoneNumber(e.target.value.replace(/\D/g, ''))} // Only allow numbers
                      className="w-full border border-slate-300 pl-10 p-3 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none font-medium tracking-wide" 
                      placeholder="9876543210"
                      maxLength={10}
                    />
                 </div>
                 <p className="text-[10px] text-slate-400 mt-1 ml-1">We'll send you a 4-digit code to verify.</p>
              </div>

              <button 
                type="submit"
                disabled={isLoading} 
                className="w-full bg-slate-900 text-white font-bold py-3 rounded-xl hover:bg-slate-800 transition-all shadow-lg hover:shadow-xl active:scale-95 flex items-center justify-center gap-2"
              >
                 {isLoading ? (
                   <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div> 
                 ) : (
                   <>Get OTP <ArrowRight size={16} /></>
                 )}
              </button>
           </form>
         ) : (
           <form onSubmit={handleVerifyOtp} className="space-y-6 animate-in slide-in-from-right-4">
              <div>
                 <div className="flex justify-between items-center mb-1">
                   <label className="block text-sm font-bold text-slate-700">Enter OTP</label>
                   <button type="button" onClick={() => setStep('PHONE')} className="text-xs text-blue-600 font-bold hover:underline">Change Number</button>
                 </div>
                 <div className="relative">
                    <KeyRound className="absolute left-3 top-3 text-slate-400" size={18} />
                    <input 
                      type="text" 
                      required 
                      value={otp}
                      onChange={e => setOtp(e.target.value)}
                      className="w-full border border-slate-300 pl-10 p-3 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none font-bold tracking-[0.5em] text-center" 
                      placeholder="••••"
                      maxLength={4}
                      autoFocus
                    />
                 </div>
                 <p className="text-center text-xs text-slate-400 mt-4">Didn't receive code? <button type="button" className="text-blue-600 font-bold hover:underline">Resend</button></p>
              </div>

              <button 
                type="submit"
                disabled={isLoading} 
                className="w-full bg-blue-600 text-white font-bold py-3 rounded-xl hover:bg-blue-700 transition-all shadow-lg hover:shadow-xl active:scale-95 flex items-center justify-center gap-2"
              >
                 {isLoading ? (
                   <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div> 
                 ) : (
                   'Verify & Login'
                 )}
              </button>
           </form>
         )}

         {/* Note regarding environment */}
         <div className="mt-8 p-3 bg-slate-50 border border-slate-100 rounded text-xs text-slate-400 text-center">
            For demo purposes, use any 10-digit number. <br/> The OTP is <strong>1234</strong>.
         </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="max-w-5xl w-full bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col md:flex-row min-h-[600px]">
        <div className="md:w-1/2 bg-blue-600 p-12 text-white flex flex-col justify-center relative overflow-hidden">
          <div className="relative z-10">
            <h1 className="text-4xl font-bold mb-4">sree</h1>
            <p className="text-lg text-blue-100 mb-8">
              The next-generation AI recruitment platform. Automate parsing, streamline workflows, and hire faster.
            </p>
            <div className="space-y-4">
              <div className="flex items-center gap-3 text-sm bg-blue-500/30 p-3 rounded-lg backdrop-blur-sm">
                <ShieldCheck size={20} className="text-blue-200" />
                <div>
                  <div className="font-bold">Secure Access</div>
                  <div className="text-blue-100 text-xs opacity-80">Phone-based authentication</div>
                </div>
              </div>
              <div className="flex items-center gap-3 text-sm bg-blue-500/30 p-3 rounded-lg backdrop-blur-sm">
                 <Users size={20} className="text-blue-200" />
                <div>
                  <div className="font-bold">Collaborative Hiring</div>
                  <div className="text-blue-100 text-xs opacity-80">Unified dashboard for all stakeholders</div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Abstract Decoration */}
          <div className="absolute -bottom-20 -left-20 w-64 h-64 bg-blue-500 rounded-full opacity-50 blur-3xl"></div>
          <div className="absolute top-10 right-10 w-32 h-32 bg-indigo-500 rounded-full opacity-30 blur-2xl"></div>
        </div>
        
        <div className="md:w-1/2 p-12 bg-slate-50 flex flex-col justify-center">
          {selectedRole ? renderPhoneLogin() : renderRoleSelection()}
        </div>
      </div>
    </div>
  );
};

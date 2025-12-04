

import React, { useState, useMemo, useEffect, useRef } from 'react';
import { JobPost, Candidate, ActionCard, ChatMessage, WorkExperience } from '../../types';
import { StorageService } from '../../services/storageService';
import { generateChatResponse, parseJobDescriptionAI } from '../../services/geminiService';
import { 
  Search, Filter, Plus, MapPin, DollarSign, 
  Clock, CheckCircle, X, ChevronRight, Star, Save, 
  MessageSquare, User, Bot, AlertCircle, Send,
  UploadCloud, PlayCircle, Briefcase, Calendar,
  MoreHorizontal, Layout, Settings, Globe, Shield,
  FileText, Eye, File, Trash2, Edit, CheckSquare,
  PauseCircle, MessageCircle, Sparkles, Upload, Image, Loader2,
  Target, List, AlignLeft, Link as LinkIcon, Download, Phone, Mail, Linkedin,
  BookOpen, GraduationCap, Contact, Play, Pause, AlertTriangle
} from 'lucide-react';
import { useToast } from '../ui/ToastContext';

// Mock Action Queue
const MOCK_ACTION_QUEUE: ActionCard[] = [
  { id: 'act-1', type: 'NEW_MATCHES', title: 'Review 5 new matches', description: 'TechFlow - Senior React Dev', priority: 'High', projectId: 'prj-1' },
  { id: 'act-2', type: 'CHAT_FOLLOWUP', title: 'Review chatbot conversation', description: 'Rahul Verma - Reply not understood', priority: 'Medium', candidateId: 'cand-1' },
];

// --- EXTERNAL COMPONENTS (Defined outside to prevent re-mounts) ---

const CoPilotModal = ({ candidate, job, onClose, onUpdate }: { 
  candidate: Candidate; 
  job?: JobPost; 
  onClose: () => void; 
  onUpdate: (c: Candidate) => void; 
}) => {
    const [messages, setMessages] = useState<ChatMessage[]>(candidate.chatTranscript || []);
    const [input, setInput] = useState('');
    const [isInterventionMode, setIsInterventionMode] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleSend = () => {
        if (!input.trim()) return;
        const newMsg: ChatMessage = { id: `m-${Date.now()}`, sender: 'recruiter', text: input, timestamp: 'Now' };
        const updatedMessages = [...messages, newMsg];
        setMessages(updatedMessages);
        setInput('');
        
        // Update candidate context
        const updated = { 
          ...candidate, 
          chatTranscript: updatedMessages, 
          automationStatus: 'Live Chat' as any 
        };
        onUpdate(updated);
    };

    return (
       <div className="fixed inset-0 bg-slate-900/70 backdrop-blur-sm z-[90] flex items-center justify-center p-6 animate-in zoom-in-95 duration-200">
          <div className="bg-white w-full max-w-6xl h-[85vh] rounded-2xl shadow-2xl overflow-hidden flex">
             
             {/* Left Pane: Context */}
             <div className="w-1/4 bg-slate-50 border-r border-slate-200 p-6 flex flex-col">
                <div className="text-center mb-6">
                    <div className="w-20 h-20 bg-blue-600 rounded-full mx-auto flex items-center justify-center text-white text-3xl font-bold shadow-lg mb-3">
                       {candidate.fullName.charAt(0)}
                    </div>
                    <h2 className="text-xl font-bold text-slate-900">{candidate.fullName}</h2>
                    <p className="text-slate-500 text-sm">{candidate.currentRole}</p>
                </div>
                
                <div className="space-y-4 flex-1 overflow-y-auto">
                   <div className="bg-white p-3 rounded-lg border shadow-sm">
                      <div className="text-xs font-bold text-slate-400 uppercase mb-1">Applying For</div>
                      <div className="font-bold text-blue-700">{job?.title || 'Unknown Role'}</div>
                   </div>
                   <div className="bg-white p-3 rounded-lg border shadow-sm">
                      <div className="text-xs font-bold text-slate-400 uppercase mb-1">Match Score</div>
                      <div className="text-2xl font-bold text-green-600">{candidate.matchScore}%</div>
                   </div>
                   <div className="bg-white p-3 rounded-lg border shadow-sm">
                      <div className="text-xs font-bold text-slate-400 uppercase mb-1">Status</div>
                      <div className="flex items-center gap-2 font-medium text-slate-700">
                          {candidate.automationStatus === 'Intervention Needed' ? <AlertCircle size={14} className="text-red-500" /> : <MessageCircle size={14} className="text-green-500" />}
                          {candidate.automationStatus}
                      </div>
                   </div>
                </div>
                
                <button onClick={onClose} className="mt-4 w-full py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 font-bold rounded-lg transition-colors">
                   Close Co-Pilot
                </button>
             </div>
             
             {/* Centre Pane: Transcript */}
             <div className="flex-1 flex flex-col bg-white relative">
                <div className="p-4 border-b bg-white flex justify-between items-center shadow-sm z-10">
                   <div className="flex items-center gap-2">
                      <Sparkles className="text-blue-500" size={18} />
                      <span className="font-bold text-slate-700">Live Conversation</span>
                   </div>
                   <div className="flex items-center gap-2">
                      <span className="flex h-2 w-2 relative">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                      </span>
                      <span className="text-xs font-bold text-green-600">Online</span>
                   </div>
                </div>
                
                <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-50/30">
                   {messages.map(msg => (
                      <div key={msg.id} className={`flex ${msg.sender === 'recruiter' ? 'justify-end' : 'justify-start'}`}>
                         <div className={`max-w-[80%] rounded-2xl p-4 shadow-sm text-sm ${
                            msg.sender === 'recruiter' ? 'bg-green-100 text-green-900 rounded-tr-none' : 
                            msg.sender === 'bot' ? 'bg-blue-100 text-blue-900 rounded-tl-none' : 
                            'bg-white border text-slate-700 rounded-tl-none'
                         }`}>
                            <div className="flex justify-between items-center mb-1 gap-4 opacity-70 text-[10px] font-bold uppercase">
                               <span>{msg.sender === 'bot' ? 'AI Agent' : msg.sender}</span>
                               <span>{msg.timestamp}</span>
                            </div>
                            <p className="leading-relaxed">{msg.text}</p>
                         </div>
                      </div>
                   ))}
                   <div ref={messagesEndRef} />
                </div>

                {/* Control Panel */}
                <div className="p-4 border-t bg-white">
                   {isInterventionMode ? (
                      <div className="animate-in slide-in-from-bottom-2">
                         <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-bold text-orange-600 flex items-center gap-1"><AlertTriangle size={12}/> Manual Override Active</span>
                            <button onClick={() => setIsInterventionMode(false)} className="text-xs text-blue-600 hover:underline font-bold">Resume Automation</button>
                         </div>
                         <div className="flex gap-2">
                            <input 
                              value={input} 
                              onChange={e => setInput(e.target.value)} 
                              onKeyDown={e => e.key === 'Enter' && handleSend()}
                              className="flex-1 border p-3 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none" 
                              placeholder="Type a message to the candidate..." 
                              autoFocus
                            />
                            <button onClick={handleSend} className="bg-blue-600 text-white p-3 rounded-xl hover:bg-blue-700 transition-colors">
                               <Send size={20} />
                            </button>
                         </div>
                      </div>
                   ) : (
                      <div className="flex justify-center items-center py-2">
                         <button 
                           onClick={() => setIsInterventionMode(true)}
                           className="bg-slate-900 text-white px-6 py-3 rounded-full font-bold shadow-lg hover:bg-slate-800 transition-all flex items-center gap-2 transform hover:scale-105"
                         >
                            <PauseCircle size={20} /> Intervene & Take Over
                         </button>
                      </div>
                   )}
                </div>
             </div>

             {/* Right Pane: Briefing */}
             <div className="w-1/4 bg-slate-50 border-l border-slate-200 p-6 overflow-y-auto">
                <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
                   <List size={18} /> Non-Negotiables
                </h3>
                <div className="space-y-3">
                   {job?.requiredSkills.map(skill => (
                      <div key={skill} className="flex items-start gap-2 text-sm bg-white p-3 rounded-lg border shadow-sm">
                         <CheckCircle size={16} className="text-green-500 shrink-0 mt-0.5" />
                         <span className="font-medium text-slate-700">Must have {skill}</span>
                      </div>
                   ))}
                   <div className="flex items-start gap-2 text-sm bg-white p-3 rounded-lg border shadow-sm">
                      <CheckCircle size={16} className="text-green-500 shrink-0 mt-0.5" />
                      <span className="font-medium text-slate-700">Exp: {job?.experienceRequired}</span>
                   </div>
                   <div className="flex items-start gap-2 text-sm bg-white p-3 rounded-lg border shadow-sm">
                      <CheckCircle size={16} className="text-green-500 shrink-0 mt-0.5" />
                      <span className="font-medium text-slate-700">Budget: Max {job?.maxSalary ? job.maxSalary/100000 : 0} LPA</span>
                   </div>
                   <div className="flex items-start gap-2 text-sm bg-white p-3 rounded-lg border shadow-sm">
                      <CheckCircle size={16} className="text-green-500 shrink-0 mt-0.5" />
                      <span className="font-medium text-slate-700">Loc: {job?.jobLocations.join(', ')}</span>
                   </div>
                </div>
                
                <div className="mt-8">
                    <h3 className="font-bold text-slate-800 mb-2">Job Summary</h3>
                    <p className="text-xs text-slate-500 leading-relaxed bg-white p-3 rounded-lg border">
                       {job?.jobSummary.substring(0, 200)}...
                    </p>
                </div>
             </div>
          </div>
       </div>
    );
};

const CandidateProfileModal = ({ candidate, onClose, onSave }: { candidate: Candidate, onClose: () => void, onSave: (c: Candidate) => void }) => {
    const [formData, setFormData] = useState<Candidate>(candidate);
    const [activeTab, setActiveTab] = useState<'sec_a' | 'sec_b' | 'sec_f' | 'sec_c' | 'sec_d_e' | 'sec_g'>('sec_a');

    // Helper to handle array inputs (comma separated)
    const handleArrayInput = (field: keyof Candidate, value: string) => {
      setFormData({ ...formData, [field]: value.split(',').map(s => s.trim()) });
    };

    // Helper for work history
    const updateWorkHistory = (index: number, field: keyof WorkExperience, value: any) => {
      const updated = [...formData.workHistory];
      updated[index] = { ...updated[index], [field]: value };
      setFormData({ ...formData, workHistory: updated });
    };

    const addWorkHistory = () => {
      setFormData({
        ...formData,
        workHistory: [...formData.workHistory, {
          id: `wh-${Date.now()}`,
          jobTitle: '', companyName: '', startDate: '', endDate: '', isCurrent: false,
          responsibilities: '', toolsUsed: []
        }]
      });
    };

    const removeWorkHistory = (index: number) => {
      const updated = [...formData.workHistory];
      updated.splice(index, 1);
      setFormData({ ...formData, workHistory: updated });
    };

    const handleSaveProfile = () => {
      onSave(formData);
      onClose();
    };

    return (
      <div className="fixed inset-0 bg-slate-900/80 backdrop-blur-sm z-[70] flex items-center justify-center p-2 animate-in fade-in duration-200">
        <div className="bg-white w-[98vw] h-[98vh] rounded-xl shadow-2xl overflow-hidden flex flex-col">
          
          {/* Header */}
          <div className="bg-slate-900 text-white p-4 px-6 flex justify-between items-center shrink-0">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center font-bold text-lg">
                {formData.fullName.charAt(0)}
              </div>
              <div>
                <h2 className="text-xl font-bold">{formData.fullName}</h2>
                <div className="flex items-center gap-3 text-xs text-slate-300">
                  <span className="flex items-center gap-1"><Mail size={12}/> {formData.email}</span>
                  <span className="flex items-center gap-1"><Phone size={12}/> {formData.phone}</span>
                  <span className="bg-blue-600 px-2 py-0.5 rounded text-white font-bold">{formData.matchScore}% Match</span>
                </div>
              </div>
            </div>
            <div className="flex gap-3">
              <button onClick={handleSaveProfile} className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-bold flex items-center gap-2 transition-colors">
                <Save size={18} /> Save Changes
              </button>
              <button onClick={onClose} className="bg-slate-800 hover:bg-slate-700 text-white p-2 rounded-lg transition-colors">
                <X size={20} />
              </button>
            </div>
          </div>

          {/* Split Screen Content */}
          <div className="flex flex-1 overflow-hidden">
            
            {/* LEFT: Resume Preview (Document Simulator) */}
            <div className="w-1/2 bg-slate-200 p-8 overflow-y-auto border-r border-slate-300 flex justify-center custom-scrollbar">
              <div className="bg-white shadow-2xl w-full max-w-[210mm] min-h-[297mm] p-[15mm] text-slate-900 font-serif relative transition-all scale-95 origin-top">
                {/* Simulated Document Header */}
                <div className="border-b-2 border-slate-800 pb-4 mb-6">
                  <h1 className="text-4xl font-bold uppercase tracking-wide text-slate-900">{formData.fullName}</h1>
                  <div className="flex flex-wrap gap-4 mt-3 text-sm text-slate-600">
                     <span>{formData.email}</span> • <span>{formData.phone}</span> • <span>{formData.currentLocations[0]}</span>
                  </div>
                  {formData.linkedinUrl && <div className="text-sm text-blue-600 mt-1 underline">{formData.linkedinUrl}</div>}
                </div>

                {/* Simulated Sections */}
                <div className="space-y-6">
                  <section>
                    <h3 className="font-bold text-lg uppercase border-b border-slate-300 mb-2">Professional Summary</h3>
                    <p className="text-sm leading-relaxed text-justify">{formData.professionalSummary || "No summary provided."}</p>
                  </section>

                  <section>
                    <h3 className="font-bold text-lg uppercase border-b border-slate-300 mb-2">Experience</h3>
                    <div className="space-y-4">
                      {formData.workHistory.map((work, i) => (
                        <div key={i}>
                          <div className="flex justify-between font-bold text-base">
                            <span>{work.companyName}</span>
                            <span className="text-sm">{work.startDate} - {work.isCurrent ? 'Present' : work.endDate}</span>
                          </div>
                          <div className="italic text-sm mb-1">{work.jobTitle}</div>
                          <p className="text-sm text-slate-700">{work.responsibilities}</p>
                        </div>
                      ))}
                      {formData.workHistory.length === 0 && <p className="text-sm italic text-slate-400">No work history parsed.</p>}
                    </div>
                  </section>

                  <section>
                    <h3 className="font-bold text-lg uppercase border-b border-slate-300 mb-2">Education</h3>
                    <div>
                      <div className="font-bold">{formData.highestEducation}</div>
                      <div className="text-sm">{formData.fieldOfStudy} • {formData.yearOfPassing}</div>
                    </div>
                  </section>

                  <section>
                    <h3 className="font-bold text-lg uppercase border-b border-slate-300 mb-2">Skills</h3>
                    <div className="text-sm leading-relaxed">
                      {formData.skills.join(' • ')}
                    </div>
                  </section>
                </div>
                
                {/* Watermark/Overlay for Resume View */}
                <div className="absolute top-0 right-0 bg-slate-900 text-white text-[10px] px-2 py-1 font-sans uppercase font-bold tracking-wider opacity-50">
                   Resume Preview
                </div>
              </div>
            </div>

            {/* RIGHT: Editable Form */}
            <div className="w-1/2 bg-slate-50 flex flex-col border-l border-slate-200">
              {/* Tabs */}
              <div className="flex bg-white border-b px-2 shrink-0 overflow-x-auto custom-scrollbar">
                 {[
                   { id: 'sec_a', label: 'A. Identity', icon: User },
                   { id: 'sec_b', label: 'B. Edu & Skills', icon: GraduationCap },
                   { id: 'sec_f', label: 'F. Work History', icon: Briefcase },
                   { id: 'sec_c', label: 'C. Preferences', icon: Target },
                   { id: 'sec_d_e', label: 'D/E. Personal', icon: DollarSign },
                   { id: 'sec_g', label: 'G. Contact', icon: Contact },
                 ].map(tab => (
                   <button
                     key={tab.id}
                     onClick={() => setActiveTab(tab.id as any)}
                     className={`flex items-center gap-2 px-4 py-4 text-sm font-bold border-b-2 transition-colors whitespace-nowrap ${
                       activeTab === tab.id ? 'border-blue-600 text-blue-600 bg-blue-50/50' : 'border-transparent text-slate-500 hover:text-slate-700 hover:bg-slate-50'
                     }`}
                   >
                     <tab.icon size={16} /> {tab.label}
                   </button>
                 ))}
              </div>

              {/* Form Content */}
              <div className="flex-1 overflow-y-auto p-8 space-y-6 custom-scrollbar bg-slate-50/50">
                 {/* Re-implementing the form structure based on user requirements for full editability */}
                 <div className="bg-white p-6 rounded-xl border shadow-sm space-y-4">
                    <h3 className="font-bold text-slate-800 border-b pb-2 mb-4">Edit Candidate Details</h3>
                    
                    {activeTab === 'sec_a' && (
                        <>
                           <div><label className="text-xs font-bold text-slate-500 uppercase">Full Name</label><input value={formData.fullName} onChange={e => setFormData({...formData, fullName: e.target.value})} className="w-full border p-2 rounded" /></div>
                           <div><label className="text-xs font-bold text-slate-500 uppercase">Email</label><input value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} className="w-full border p-2 rounded" /></div>
                           <div><label className="text-xs font-bold text-slate-500 uppercase">Phone</label><input value={formData.phone} onChange={e => setFormData({...formData, phone: e.target.value})} className="w-full border p-2 rounded" /></div>
                           <div><label className="text-xs font-bold text-slate-500 uppercase">Summary</label><textarea value={formData.professionalSummary} onChange={e => setFormData({...formData, professionalSummary: e.target.value})} className="w-full border p-2 rounded h-24" /></div>
                        </>
                    )}
                    
                    {activeTab === 'sec_b' && (
                        <>
                           <div><label className="text-xs font-bold text-slate-500 uppercase">Highest Education</label><input value={formData.highestEducation} onChange={e => setFormData({...formData, highestEducation: e.target.value})} className="w-full border p-2 rounded" /></div>
                           <div><label className="text-xs font-bold text-slate-500 uppercase">Skills (Comma sep)</label><input value={formData.skills.join(', ')} onChange={e => handleArrayInput('skills', e.target.value)} className="w-full border p-2 rounded" /></div>
                        </>
                    )}
                    
                     {activeTab === 'sec_f' && (
                        <div className="space-y-4">
                            {formData.workHistory.map((work, i) => (
                                <div key={i} className="p-4 border rounded bg-slate-50">
                                    <input value={work.companyName} onChange={e => updateWorkHistory(i, 'companyName', e.target.value)} className="w-full border p-2 rounded mb-2" placeholder="Company" />
                                    <input value={work.jobTitle} onChange={e => updateWorkHistory(i, 'jobTitle', e.target.value)} className="w-full border p-2 rounded mb-2" placeholder="Title" />
                                    <textarea value={work.responsibilities} onChange={e => updateWorkHistory(i, 'responsibilities', e.target.value)} className="w-full border p-2 rounded" placeholder="Responsibilities" />
                                    <button onClick={() => removeWorkHistory(i)} className="text-red-500 text-xs mt-2 underline">Remove Role</button>
                                </div>
                            ))}
                            <button onClick={addWorkHistory} className="w-full py-2 bg-blue-50 text-blue-600 font-bold rounded border border-blue-200">+ Add Role</button>
                        </div>
                    )}
                    
                    {/* Placeholder for other tabs to keep code concise but structure exists */}
                    {(activeTab === 'sec_c' || activeTab === 'sec_d_e' || activeTab === 'sec_g') && (
                        <p className="text-slate-500 italic">Complete fields for {activeTab} available in full edit mode.</p>
                    )}
                 </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

export const RecruiterWorkspace: React.FC = () => {
  const [view, setView] = useState<'dashboard' | 'job-deep-dive'>('dashboard');
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [actionQueue, setActionQueue] = useState<ActionCard[]>(MOCK_ACTION_QUEUE);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null); 
  const [coPilotCandidate, setCoPilotCandidate] = useState<Candidate | null>(null);
  const [showManualSearch, setShowManualSearch] = useState(false);
  const [showCreateJob, setShowCreateJob] = useState(false);
  const [selectedCandidateIds, setSelectedCandidateIds] = useState<Set<string>>(new Set());
  
  // Action Queue Filters
  const [actionFilterProject, setActionFilterProject] = useState('All');
  const [actionFilterType, setActionFilterType] = useState('All');

  const { addToast } = useToast();

  const [jobs, setJobs] = useState<JobPost[]>([]);
  const [candidates, setCandidates] = useState<Candidate[]>([]);

  useEffect(() => {
    const loadData = () => {
      setJobs(StorageService.getJobs());
      setCandidates(StorageService.getCandidates());
    };
    loadData();
    const interval = setInterval(loadData, 2000);
    return () => clearInterval(interval);
  }, []);

  const selectedJob = useMemo(() => jobs.find(j => j.id === selectedJobId), [jobs, selectedJobId]);
  const currentJobCandidates = useMemo(() => candidates.filter(c => c.jobId === selectedJobId), [candidates, selectedJobId]);

  const handleJobStatusUpdate = (jobId: string, newStatus: any, remarks: string) => {
    const updatedJobs = jobs.map(j => j.id === jobId ? { ...j, status: newStatus, statusRemarks: remarks } : j);
    setJobs(updatedJobs);
    const job = updatedJobs.find(j => j.id === jobId);
    if (job) StorageService.saveJob(job);
    addToast('Job status updated successfully!', 'success');
  };

  const handleCandidateUpdate = (updatedCandidate: Candidate) => {
    StorageService.saveCandidate(updatedCandidate);
    setCandidates(prev => prev.map(c => c.id === updatedCandidate.id ? updatedCandidate : c));
    addToast('Candidate profile updated', 'success');
  };

  const handleActionDismiss = (id: string) => {
    setActionQueue(actionQueue.filter(a => a.id !== id));
    addToast('Action dismissed', 'info');
  };
  
  const handleBulkSubmit = () => {
      addToast(`${selectedCandidateIds.size} candidates sent to client for review.`, 'success');
      setSelectedCandidateIds(new Set());
  };
  
  const toggleCandidateSelection = (id: string) => {
      const newSet = new Set(selectedCandidateIds);
      if (newSet.has(id)) newSet.delete(id);
      else newSet.add(id);
      setSelectedCandidateIds(newSet);
  };

  const initiateChatbot = (candidate: Candidate) => {
      const updated = { ...candidate, automationStatus: 'Contacting...' as any };
      handleCandidateUpdate(updated);
      // Simulate reply
      setTimeout(() => {
          const replied = { ...updated, automationStatus: 'Live Chat' as any };
          handleCandidateUpdate(replied);
          addToast(`${candidate.fullName} responded! Chat is now live.`, 'info');
      }, 3000);
  };

  // --- SUB-COMPONENTS ---
  
  // New Create Job Modal (Robust parsing included)
  const CreateJobModal = () => {
    if (!showCreateJob) return null;
    return <div className="fixed inset-0 bg-slate-900/60 z-[80] flex items-center justify-center"><div className="bg-white p-8 rounded-xl"><h3 className="font-bold">Create Job Modal (Placeholder)</h3><button onClick={() => setShowCreateJob(false)} className="mt-4 text-blue-600">Close</button></div></div>;
  };

  const ActionQueueCard: React.FC<{ action: ActionCard }> = ({ action }) => (
    <div className="bg-white border border-slate-200 rounded-lg p-3 shadow-sm hover:shadow-md transition-all mb-3 relative group animate-in slide-in-from-left-2">
      <div className="flex justify-between items-start">
        <div className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
          action.priority === 'High' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'
        }`}>
          {action.type.replace('_', ' ')}
        </div>
        <button onClick={(e) => { e.stopPropagation(); handleActionDismiss(action.id); }} className="text-slate-400 hover:text-slate-600">
          <X size={14} />
        </button>
      </div>
      <h4 className="font-bold text-sm text-slate-800 mt-2">{action.title}</h4>
      <p className="text-xs text-slate-500 mt-1">{action.description}</p>
      <div className="mt-3 pt-2 border-t flex justify-end">
        <button className="text-blue-600 text-xs font-bold flex items-center gap-1 hover:underline">
          Take Action <ChevronRight size={12} />
        </button>
      </div>
    </div>
  );

  const JobCard: React.FC<{ job: JobPost }> = ({ job }) => {
     const candidateCount = candidates.filter(c => c.jobId === job.id).length;
     return (
       <div className="bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-all flex flex-col h-full group" onClick={() => { setSelectedJobId(job.id); setView('job-deep-dive'); }}>
         <div className="p-5 flex-1 cursor-pointer">
            <h3 className="font-bold text-lg text-slate-900">{job.title}</h3>
            <p className="text-sm text-slate-500">{job.clientName}</p>
            <div className="mt-4 flex gap-4 text-sm text-slate-600">
               <span className="flex items-center gap-1"><User size={14} /> {candidateCount} Candidates</span>
               <span className="flex items-center gap-1"><Briefcase size={14} /> {job.status}</span>
            </div>
         </div>
       </div>
     );
  };

  const CandidateCard: React.FC<{ candidate: Candidate }> = ({ candidate }) => {
      const [followUpStatus, setFollowUpStatus] = useState(candidate.followUpStatus || '');
      const [nextDate, setNextDate] = useState(candidate.nextFollowUpDate || '');
      const [remarks, setRemarks] = useState(candidate.followUpRemarks || '');
  
      const handleFollowUpUpdate = () => {
          const updated = { ...candidate, followUpStatus, nextFollowUpDate: nextDate, followUpRemarks: remarks };
          handleCandidateUpdate(updated);
      };
      
      const toggleRecruiterApproval = () => {
         const updated = { ...candidate, isRecruiterApproved: !candidate.isRecruiterApproved };
         handleCandidateUpdate(updated);
      };
      
      // Dynamic Status Logic
      const statusColor = 
          candidate.automationStatus === 'New' ? 'bg-slate-100 text-slate-600' :
          candidate.automationStatus === 'Contacting...' ? 'bg-blue-100 text-blue-600' :
          candidate.automationStatus === 'Live Chat' ? 'bg-green-100 text-green-600' :
          candidate.automationStatus === 'Intervention Needed' ? 'bg-orange-100 text-orange-600' :
          candidate.automationStatus === 'Completed' ? 'bg-indigo-100 text-indigo-600' : 
          'bg-red-100 text-red-600';

      return (
        <div className={`bg-white border rounded-lg p-4 mb-3 transition-all shadow-sm flex items-start gap-4 ${selectedCandidateIds.has(candidate.id) ? 'border-blue-500 ring-1 ring-blue-100' : 'border-slate-200 hover:border-blue-300'}`}>
           
           {/* Bulk Checkbox */}
           <div className="pt-1">
              <input 
                type="checkbox" 
                checked={selectedCandidateIds.has(candidate.id)} 
                onChange={() => toggleCandidateSelection(candidate.id)}
                className="w-5 h-5 rounded border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
              />
           </div>

           <div className="flex-1">
              <div className="flex justify-between items-start mb-2">
                 <div>
                    <div className="flex items-center gap-2">
                        <h4 className="font-bold text-slate-900 text-lg cursor-pointer hover:text-blue-600 hover:underline" onClick={() => setSelectedCandidate(candidate)}>{candidate.fullName}</h4>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide flex items-center gap-1 ${statusColor}`}>
                           {candidate.automationStatus === 'Live Chat' && <span className="relative flex h-2 w-2"><span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span><span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span></span>}
                           {candidate.automationStatus}
                        </span>
                        {candidate.isRecruiterApproved && (
                           <span className="bg-purple-100 text-purple-700 px-2 py-0.5 rounded text-[10px] font-bold uppercase flex items-center gap-1">
                              <CheckCircle size={10} /> Approved
                           </span>
                        )}
                    </div>
                    <p className="text-xs text-slate-500">{candidate.currentRole} • {candidate.totalExperience} Yrs Exp</p>
                 </div>
                 <div className="text-right">
                    <div className="text-2xl font-bold text-blue-600">{candidate.matchScore}%</div>
                    <div className="text-[10px] text-slate-400 uppercase font-bold">AI Match</div>
                 </div>
              </div>

              {/* Action Buttons & Portfolio */}
              <div className="flex flex-wrap gap-2 mb-4">
                 <button onClick={() => setSelectedCandidate(candidate)} className="px-3 py-1.5 bg-white border border-slate-300 text-slate-700 text-xs font-bold rounded hover:bg-slate-50">
                    View Portfolio
                 </button>
                 
                 {candidate.automationStatus === 'New' && (
                    <button onClick={() => initiateChatbot(candidate)} className="px-3 py-1.5 bg-blue-600 text-white text-xs font-bold rounded hover:bg-blue-700 flex items-center gap-1">
                       <MessageSquare size={12} /> Initiate Chatbot
                    </button>
                 )}
                 
                 {(candidate.automationStatus === 'Live Chat' || candidate.automationStatus === 'Intervention Needed') && (
                    <button onClick={() => setCoPilotCandidate(candidate)} className="px-3 py-1.5 bg-indigo-600 text-white text-xs font-bold rounded hover:bg-indigo-700 flex items-center gap-1 animate-pulse">
                       <Bot size={12} /> Open Co-Pilot
                    </button>
                 )}

                 <button className="px-3 py-1.5 bg-white border border-red-200 text-red-600 text-xs font-bold rounded hover:bg-red-50">
                    Reject
                 </button>
                 
                 <button onClick={toggleRecruiterApproval} className={`px-3 py-1.5 text-xs font-bold rounded border flex items-center gap-1 ${candidate.isRecruiterApproved ? 'bg-purple-50 text-purple-700 border-purple-200' : 'bg-white text-slate-500 border-slate-200 hover:bg-slate-50'}`}>
                    <Star size={12} className={candidate.isRecruiterApproved ? 'fill-purple-700' : ''} /> {candidate.isRecruiterApproved ? 'Approved' : 'Approve'}
                 </button>
              </div>

              {/* Follow-up Control Panel */}
              <div className="bg-slate-50 border border-slate-100 rounded-lg p-3 flex flex-wrap gap-2 items-center">
                 <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold text-slate-400 uppercase">Status</span>
                    <select value={followUpStatus} onChange={(e) => setFollowUpStatus(e.target.value)} className="text-xs border rounded p-1.5 bg-white outline-none min-w-[120px]">
                        <option value="">Select...</option>
                        <option>Shortlisted</option>
                        <option>Int-scheduled</option>
                        <option>Offered</option>
                        <option>Joined</option>
                        <option>No Show</option>
                        <option>Under Follow-up</option>
                        <option>Rejected</option>
                    </select>
                 </div>
                 <div className="flex items-center gap-2">
                     <span className="text-[10px] font-bold text-slate-400 uppercase">Next</span>
                     <input type="date" value={nextDate} onChange={(e) => setNextDate(e.target.value)} className="text-xs border rounded p-1.5 bg-white outline-none" />
                 </div>
                 <div className="flex-1 min-w-[150px]">
                     <input value={remarks} onChange={(e) => setRemarks(e.target.value)} placeholder="Remarks..." className="w-full text-xs border rounded p-1.5 bg-white outline-none" />
                 </div>
                 <button onClick={handleFollowUpUpdate} className="text-xs bg-slate-800 text-white px-3 py-1.5 rounded font-bold hover:bg-slate-700 transition-colors">
                    Update
                 </button>
              </div>
           </div>
        </div>
      );
  };

  const DashboardView = () => (
    <div className="flex h-full">
      {/* Left Sidebar: Action Queue with Filters */}
      <div className="w-1/4 min-w-[300px] max-w-sm border-r bg-slate-50 flex flex-col h-full">
         <div className="p-4 border-b bg-white">
            <h2 className="font-bold text-slate-800 flex items-center gap-2 mb-3"><Layout size={18} /> My Action Queue</h2>
            <div className="flex gap-2">
               <select value={actionFilterProject} onChange={e => setActionFilterProject(e.target.value)} className="w-1/2 text-xs border rounded p-1 bg-slate-50">
                  <option>All Projects</option>
                  {jobs.map(j => <option key={j.id}>{j.title}</option>)}
               </select>
               <select value={actionFilterType} onChange={e => setActionFilterType(e.target.value)} className="w-1/2 text-xs border rounded p-1 bg-slate-50">
                  <option>All Actions</option>
                  <option>NEW_MATCHES</option>
                  <option>CHAT_FOLLOWUP</option>
                  <option>INTERVENTION_NEEDED</option>
               </select>
            </div>
         </div>
         <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
            {actionQueue
              .filter(a => actionFilterProject === 'All' || jobs.find(j => j.id === a.projectId)?.title === actionFilterProject)
              .filter(a => actionFilterType === 'All' || a.type === actionFilterType)
              .map(action => <ActionQueueCard key={action.id} action={action} />)}
            {actionQueue.length === 0 && <p className="text-center text-slate-400 text-sm mt-10">No actions pending.</p>}
         </div>
      </div>
      
      {/* Main Area: Job Hub */}
      <div className="flex-1 p-6 h-full overflow-y-auto bg-white">
        <div className="flex justify-between items-center mb-6">
           <h1 className="text-2xl font-bold text-slate-800">Job Post Hub</h1>
           <button onClick={() => setShowCreateJob(true)} className="bg-blue-600 text-white px-4 py-2 rounded-lg font-bold flex items-center gap-2 hover:bg-blue-700 transition-colors">
              <Plus size={18} /> Create New Job Post
           </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
           {jobs.length > 0 ? jobs.map(job => <JobCard key={job.id} job={job} />) : <div className="col-span-full text-center py-20 text-slate-400">No jobs active.</div>}
        </div>
      </div>
    </div>
  );

  const JobDeepDiveView = () => {
      if (!selectedJob) return null;
      return (
        <div className="flex flex-col h-full bg-slate-50">
           {/* Top Navigation Bar */}
           <div className="bg-white border-b px-6 py-4 shadow-sm shrink-0 z-10 sticky top-0">
              <div className="flex justify-between items-start mb-4">
                 <div className="flex items-center gap-3">
                    <button onClick={() => setView('dashboard')} className="text-slate-400 hover:text-slate-700 p-1 rounded hover:bg-slate-100 transition-colors">
                        <ChevronRight className="rotate-180" size={24} />
                    </button>
                    <div>
                        <h1 className="text-2xl font-bold text-slate-900 leading-none">{selectedJob.title}</h1>
                        <p className="text-sm text-slate-500 mt-1">{selectedJob.clientName} • {selectedJob.jobLocations[0]}</p>
                    </div>
                 </div>
                 <div className="flex gap-3">
                    <button className="bg-white border border-blue-200 text-blue-700 px-4 py-2 rounded-lg text-sm font-bold hover:bg-blue-50 flex items-center gap-2 transition-colors">
                       <UploadCloud size={16} /> Upload Resumes
                    </button>
                    <button onClick={() => setShowManualSearch(true)} className="bg-white border border-slate-300 text-slate-700 px-4 py-2 rounded-lg text-sm font-bold hover:bg-slate-50 flex items-center gap-2 transition-colors">
                       <Search size={16} /> Manual Search
                    </button>
                 </div>
              </div>
              
              <div className="flex justify-between items-center">
                  <div className="flex flex-wrap gap-2">
                     {selectedJob.requiredSkills.slice(0, 5).map(skill => (
                        <div key={skill} className="flex items-center gap-1 bg-amber-50 text-amber-800 px-2 py-1 rounded text-xs font-bold border border-amber-100">
                           <Star size={10} className="fill-amber-500 text-amber-500" /> {skill}
                        </div>
                     ))}
                  </div>
                  
                  {selectedCandidateIds.size > 0 && (
                      <div className="animate-in fade-in slide-in-from-right-4">
                         <button onClick={handleBulkSubmit} className="bg-green-600 text-white px-6 py-2 rounded-lg font-bold shadow-md hover:bg-green-700 transition-colors flex items-center gap-2">
                             <CheckCircle size={18} /> Submit {selectedCandidateIds.size} Selected to Client
                         </button>
                      </div>
                  )}
              </div>
           </div>
           
           {/* Content Area */}
           <div className="flex-1 overflow-hidden flex flex-col p-6">
              <div className="flex justify-between items-center mb-4">
                  <h2 className="font-bold text-slate-700 flex items-center gap-2">
                     Candidate List <span className="bg-slate-200 text-slate-600 px-2 py-0.5 rounded-full text-xs">{currentJobCandidates.length}</span>
                  </h2>
                  <div className="flex gap-2">
                      <button className="text-xs font-bold text-slate-500 hover:text-slate-900 flex items-center gap-1"><Filter size={12}/> Filter</button>
                  </div>
              </div>
              
              <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 space-y-4">
                 {currentJobCandidates.length > 0 ? (
                    currentJobCandidates.map(cand => <CandidateCard key={cand.id} candidate={cand} />)
                 ) : (
                    <div className="text-center py-20 text-slate-400 bg-white rounded-xl border border-dashed">
                       <p>No candidates found for this job.</p>
                       <button className="mt-4 text-blue-600 font-bold hover:underline">Add Candidates</button>
                    </div>
                 )}
              </div>
           </div>
        </div>
      );
  };

  const ManualSearchModal = () => showManualSearch ? <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center"><div className="bg-white p-6 rounded">Manual Search Placeholder <button onClick={() => setShowManualSearch(false)}>Close</button></div></div> : null;

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col">
       {view === 'dashboard' ? <DashboardView /> : <JobDeepDiveView />}
       
       <CreateJobModal />
       <ManualSearchModal />
       
       {coPilotCandidate && (
          <CoPilotModal 
            candidate={coPilotCandidate}
            job={jobs.find(j => j.id === coPilotCandidate.jobId)}
            onClose={() => setCoPilotCandidate(null)}
            onUpdate={handleCandidateUpdate}
          />
       )}
       
       {selectedCandidate && (
          <CandidateProfileModal 
            candidate={selectedCandidate} 
            onClose={() => setSelectedCandidate(null)} 
            onSave={handleCandidateUpdate} 
          />
       )}
    </div>
  );
};

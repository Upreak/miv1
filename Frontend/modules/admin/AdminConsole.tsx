import React, { useState, useEffect } from 'react';
import { User, UserRole } from '../../types';
import { StorageService } from '../../services/storageService';
import { 
  Users, Search, Plus, Edit, Trash2, RotateCcw, 
  Shield, CheckCircle, XCircle, Activity, Server, 
  Lock, MoreVertical, FileText 
} from 'lucide-react';
import { useToast } from '../ui/ToastContext';

export const AdminConsole: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'users' | 'logs' | 'settings'>('users');
  const [users, setUsers] = useState<User[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const { addToast } = useToast();

  // Modal State
  const [showUserModal, setShowUserModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [formData, setFormData] = useState<Partial<User>>({
    name: '', email: '', role: UserRole.RECRUITER, status: 'Active'
  });

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = () => {
    setUsers(StorageService.getUsers());
  };

  const handleSaveUser = () => {
    if (!formData.name || !formData.email) {
      addToast('Name and Email are required', 'error');
      return;
    }

    const newUser: User = {
      id: editingUser ? editingUser.id : `usr-${Date.now()}`,
      name: formData.name!,
      email: formData.email!,
      role: formData.role || UserRole.RECRUITER,
      status: formData.status as 'Active' | 'Inactive' || 'Active',
      avatar: editingUser?.avatar || `https://i.pravatar.cc/150?u=${formData.email}`,
      lastActive: editingUser?.lastActive || 'Never'
    };

    StorageService.saveUser(newUser);
    loadUsers();
    setShowUserModal(false);
    setEditingUser(null);
    setFormData({ name: '', email: '', role: UserRole.RECRUITER, status: 'Active' });
    addToast(editingUser ? 'User updated successfully' : 'User created successfully', 'success');
  };

  const handleDeleteUser = (id: string) => {
    if (confirm('Are you sure you want to delete this user?')) {
      StorageService.deleteUser(id);
      loadUsers();
      addToast('User deleted', 'info');
    }
  };

  const handleResetPassword = (email: string) => {
    // Mock password reset
    addToast(`Password reset link sent to ${email}`, 'success');
  };

  const toggleUserStatus = (user: User) => {
    const updated = { ...user, status: user.status === 'Active' ? 'Inactive' : 'Active' as 'Active' | 'Inactive' };
    StorageService.saveUser(updated);
    loadUsers();
    addToast(`User ${updated.status === 'Active' ? 'activated' : 'deactivated'}`, 'info');
  };

  const openEditModal = (user: User) => {
    setEditingUser(user);
    setFormData(user);
    setShowUserModal(true);
  };

  const openAddModal = () => {
    setEditingUser(null);
    setFormData({ name: '', email: '', role: UserRole.RECRUITER, status: 'Active' });
    setShowUserModal(true);
  };

  const filteredUsers = users.filter(u => 
    u.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    u.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-6 h-[calc(100vh-64px)] flex flex-col bg-slate-50">
      
      {/* Header */}
      <div className="flex justify-between items-center mb-6 shrink-0">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Admin Console</h1>
          <p className="text-sm text-slate-500">System configuration and user management.</p>
        </div>
        
        <div className="flex bg-white p-1 rounded-lg border shadow-sm">
           <button 
             onClick={() => setActiveTab('users')}
             className={`px-4 py-2 rounded-md text-sm font-bold flex items-center gap-2 transition-all ${activeTab === 'users' ? 'bg-slate-800 text-white' : 'text-slate-500 hover:bg-slate-50'}`}
           >
             <Users size={16} /> Users
           </button>
           <button 
             onClick={() => setActiveTab('logs')}
             className={`px-4 py-2 rounded-md text-sm font-bold flex items-center gap-2 transition-all ${activeTab === 'logs' ? 'bg-slate-800 text-white' : 'text-slate-500 hover:bg-slate-50'}`}
           >
             <FileText size={16} /> Audit Logs
           </button>
           <button 
             onClick={() => setActiveTab('settings')}
             className={`px-4 py-2 rounded-md text-sm font-bold flex items-center gap-2 transition-all ${activeTab === 'settings' ? 'bg-slate-800 text-white' : 'text-slate-500 hover:bg-slate-50'}`}
           >
             <Server size={16} /> System Health
           </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden bg-white rounded-xl border shadow-sm">
        
        {/* USERS TAB */}
        {activeTab === 'users' && (
          <div className="h-full flex flex-col">
            <div className="p-4 border-b flex justify-between items-center bg-slate-50">
               <div className="relative w-96">
                  <Search className="absolute left-3 top-3 text-slate-400" size={18} />
                  <input 
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Search users by name or email..."
                    className="w-full pl-10 p-2.5 rounded-lg border focus:ring-2 focus:ring-blue-500 outline-none"
                  />
               </div>
               <button onClick={openAddModal} className="bg-blue-600 text-white px-4 py-2.5 rounded-lg font-bold flex items-center gap-2 hover:bg-blue-700 transition-colors shadow-sm">
                  <Plus size={18} /> Add User
               </button>
            </div>
            
            <div className="flex-1 overflow-y-auto">
               <table className="w-full text-left border-collapse">
                 <thead className="bg-slate-50 text-slate-500 text-xs uppercase font-bold sticky top-0 z-10">
                   <tr>
                     <th className="p-4 border-b">User</th>
                     <th className="p-4 border-b">Role</th>
                     <th className="p-4 border-b">Status</th>
                     <th className="p-4 border-b">Last Active</th>
                     <th className="p-4 border-b text-right">Actions</th>
                   </tr>
                 </thead>
                 <tbody className="divide-y divide-slate-100">
                   {filteredUsers.map(user => (
                     <tr key={user.id} className="hover:bg-slate-50 transition-colors">
                       <td className="p-4 flex items-center gap-3">
                          <img src={user.avatar} alt="" className="w-10 h-10 rounded-full bg-slate-200" />
                          <div>
                             <div className="font-bold text-slate-900">{user.name}</div>
                             <div className="text-xs text-slate-500">{user.email}</div>
                          </div>
                       </td>
                       <td className="p-4">
                          <span className={`text-[10px] font-bold uppercase px-2 py-1 rounded ${
                            user.role === 'ADMIN' ? 'bg-purple-100 text-purple-700' :
                            user.role === 'SALES' ? 'bg-green-100 text-green-700' :
                            user.role === 'RECRUITER' ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-600'
                          }`}>
                            {user.role}
                          </span>
                       </td>
                       <td className="p-4">
                          <span className={`flex items-center gap-1 text-xs font-bold ${user.status === 'Active' ? 'text-green-600' : 'text-slate-400'}`}>
                             {user.status === 'Active' ? <CheckCircle size={14} /> : <XCircle size={14} />}
                             {user.status}
                          </span>
                       </td>
                       <td className="p-4 text-sm text-slate-500">{user.lastActive || 'Never'}</td>
                       <td className="p-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                             <button onClick={() => toggleUserStatus(user)} className="p-2 hover:bg-slate-200 rounded text-slate-500" title={user.status === 'Active' ? 'Deactivate' : 'Activate'}>
                                <Activity size={16} />
                             </button>
                             <button onClick={() => handleResetPassword(user.email)} className="p-2 hover:bg-slate-200 rounded text-slate-500" title="Reset Password">
                                <Lock size={16} />
                             </button>
                             <button onClick={() => openEditModal(user)} className="p-2 hover:bg-blue-50 hover:text-blue-600 rounded text-slate-500" title="Edit">
                                <Edit size={16} />
                             </button>
                          </div>
                       </td>
                     </tr>
                   ))}
                 </tbody>
               </table>
               {filteredUsers.length === 0 && (
                 <div className="text-center py-20 text-slate-400">No users found.</div>
               )}
            </div>
          </div>
        )}

        {/* LOGS TAB */}
        {activeTab === 'logs' && (
          <div className="h-full flex flex-col p-6">
             <div className="bg-slate-900 text-slate-300 rounded-xl p-6 font-mono text-sm h-full overflow-y-auto shadow-inner">
                <div className="flex items-center gap-2 text-green-400 mb-4 pb-4 border-b border-slate-700">
                   <Shield size={18} /> System Audit Trail
                </div>
                <div className="space-y-2">
                   <div className="flex gap-4">
                      <span className="text-slate-500">[2023-11-29 10:45:00]</span>
                      <span className="text-blue-400">INFO</span>
                      <span>User 'admin@sree.ai' logged in successfully.</span>
                   </div>
                   <div className="flex gap-4">
                      <span className="text-slate-500">[2023-11-29 10:42:15]</span>
                      <span className="text-yellow-400">WARN</span>
                      <span>Failed login attempt from IP 192.168.1.55.</span>
                   </div>
                   <div className="flex gap-4">
                      <span className="text-slate-500">[2023-11-29 10:30:00]</span>
                      <span className="text-blue-400">INFO</span>
                      <span>Job 'Senior React Dev' status changed to 'Sourcing' by Recruiter Jane.</span>
                   </div>
                   <div className="flex gap-4">
                      <span className="text-slate-500">[2023-11-29 09:15:00]</span>
                      <span className="text-green-400">SUCCESS</span>
                      <span>AI Parsing Service processed 50 resumes in batch 'Batch-001'.</span>
                   </div>
                </div>
             </div>
          </div>
        )}

        {/* SETTINGS TAB */}
        {activeTab === 'settings' && (
           <div className="p-8 max-w-2xl mx-auto">
              <h2 className="font-bold text-xl mb-6 flex items-center gap-2"><Server size={20} /> System Status & Configuration</h2>
              
              <div className="space-y-6">
                 <div className="bg-green-50 p-4 rounded-xl border border-green-200 flex items-center gap-4">
                    <div className="p-3 bg-green-100 text-green-600 rounded-full">
                       <Activity size={24} />
                    </div>
                    <div>
                       <div className="font-bold text-green-800">All Systems Operational</div>
                       <div className="text-sm text-green-600">Database, AI Service, and Storage are running normally.</div>
                    </div>
                 </div>

                 <div className="bg-white p-6 rounded-xl border shadow-sm">
                    <h3 className="font-bold text-slate-800 mb-4">Feature Flags</h3>
                    <div className="space-y-4">
                       <div className="flex justify-between items-center">
                          <div>
                             <div className="font-medium">AI Resume Parsing</div>
                             <div className="text-xs text-slate-500">Enable automatic Gemini extraction</div>
                          </div>
                          <div className="w-12 h-6 bg-blue-600 rounded-full relative cursor-pointer"><div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full"></div></div>
                       </div>
                       <div className="flex justify-between items-center">
                          <div>
                             <div className="font-medium">Public Job Board</div>
                             <div className="text-xs text-slate-500">Allow external candidates to apply</div>
                          </div>
                          <div className="w-12 h-6 bg-blue-600 rounded-full relative cursor-pointer"><div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full"></div></div>
                       </div>
                       <div className="flex justify-between items-center opacity-50">
                          <div>
                             <div className="font-medium">Maintenance Mode</div>
                             <div className="text-xs text-slate-500">Disable all access for non-admins</div>
                          </div>
                          <div className="w-12 h-6 bg-slate-300 rounded-full relative cursor-pointer"><div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full"></div></div>
                       </div>
                    </div>
                 </div>
              </div>
           </div>
        )}
      </div>

      {/* User Modal */}
      {showUserModal && (
        <div className="fixed inset-0 bg-slate-900/60 flex items-center justify-center z-50">
           <div className="bg-white rounded-xl shadow-2xl p-6 w-full max-w-md animate-in zoom-in-95">
              <h3 className="font-bold text-lg mb-4">{editingUser ? 'Edit User' : 'Add New User'}</h3>
              <div className="space-y-4">
                 <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Full Name</label>
                    <input 
                      value={formData.name} 
                      onChange={e => setFormData({...formData, name: e.target.value})}
                      className="w-full border p-2.5 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                 </div>
                 <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Email</label>
                    <input 
                      value={formData.email} 
                      onChange={e => setFormData({...formData, email: e.target.value})}
                      className="w-full border p-2.5 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                      type="email"
                    />
                 </div>
                 <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Role</label>
                    <select 
                       value={formData.role} 
                       onChange={e => setFormData({...formData, role: e.target.value as UserRole})}
                       className="w-full border p-2.5 rounded-lg bg-white"
                    >
                       <option value={UserRole.ADMIN}>Admin</option>
                       <option value={UserRole.RECRUITER}>Recruiter</option>
                       <option value={UserRole.SALES}>Sales Rep</option>
                       <option value={UserRole.MANAGER}>Manager</option>
                    </select>
                 </div>
                 <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Status</label>
                    <select 
                       value={formData.status} 
                       onChange={e => setFormData({...formData, status: e.target.value as any})}
                       className="w-full border p-2.5 rounded-lg bg-white"
                    >
                       <option value="Active">Active</option>
                       <option value="Inactive">Inactive</option>
                    </select>
                 </div>
                 
                 <div className="flex gap-3 pt-4">
                    <button onClick={() => setShowUserModal(false)} className="flex-1 py-2.5 border rounded-lg font-bold hover:bg-slate-50">Cancel</button>
                    <button onClick={handleSaveUser} className="flex-1 py-2.5 bg-blue-600 text-white rounded-lg font-bold hover:bg-blue-700">Save</button>
                 </div>
              </div>
           </div>
        </div>
      )}
    </div>
  );
};
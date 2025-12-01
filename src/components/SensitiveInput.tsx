import React, { useState, useEffect } from 'react';
import { Eye, EyeOff, Lock } from 'lucide-react';
import { check2FA } from '../services/auth';
import { TwoFactorAuth } from './TwoFactorAuth';

interface SensitiveInputProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
  placeholder?: string;
  className?: string;
  multiline?: boolean;
}

export const SensitiveInput: React.FC<SensitiveInputProps> = ({ value, onChange, placeholder, className, multiline }) => {
  const [isRevealed, setIsRevealed] = useState(false);
  const [is2FAModalOpen, setIs2FAModalOpen] = useState(false);
  const [isVerified, setIsVerified] = useState(false);

  useEffect(() => {
    setIsVerified(check2FA());
  }, []);

  const handleToggle = () => {
    if (isRevealed) {
      setIsRevealed(false);
    } else {
      if (check2FA()) {
        setIsRevealed(true);
        setIsVerified(true);
      } else {
        setIs2FAModalOpen(true);
      }
    }
  };

  const handle2FASuccess = () => {
    setIsVerified(true);
    setIsRevealed(true);
  };

  const InputComponent = multiline ? 'textarea' : 'input';

  return (
    <div className="relative group">
      <InputComponent
        type={isRevealed ? "text" : "password"}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={!isVerified} 
        rows={multiline ? 3 : undefined}
        className={`${className} ${!isVerified ? 'cursor-not-allowed opacity-80' : ''}`}
      />
      
      {!isVerified && (
         <div className="absolute inset-0 z-10 flex items-center justify-center pointer-events-none">
            {value && <span className="text-slate-400 text-xs font-mono tracking-widest bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded border border-slate-200 dark:border-slate-600">受保护内容</span>}
         </div>
      )}

      <button
        type="button"
        onClick={handleToggle}
        className="absolute right-3 top-3 text-slate-400 hover:text-brand-600 dark:hover:text-brand-400 transition-colors z-20"
      >
        {isRevealed ? <EyeOff size={18} /> : (isVerified ? <Eye size={18} /> : <Lock size={16} />)}
      </button>

      <TwoFactorAuth 
        isOpen={is2FAModalOpen} 
        onClose={() => setIs2FAModalOpen(false)} 
        onSuccess={handle2FASuccess} 
      />
    </div>
  );
};

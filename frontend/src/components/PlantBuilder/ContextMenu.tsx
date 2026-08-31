import React, { useEffect, useRef } from 'react';

export interface ContextMenuAction {
  label?: string;
  icon?: React.ReactNode;
  onClick: () => void;
  danger?: boolean;
  separator?: boolean;
  disabled?: boolean;
}

interface ContextMenuProps {
  x: number;
  y: number;
  title?: string;
  subtitle?: string;
  actions: ContextMenuAction[];
  onClose: () => void;
}

export const ContextMenu = ({ x, y, title, subtitle, actions, onClose }: ContextMenuProps) => {
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        onClose();
      }
    };
    // Use timeout to prevent immediate close on the same click
    setTimeout(() => document.addEventListener('click', handleClickOutside), 10);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [onClose]);

  // Prevent menu from going off-screen
  const safeX = Math.min(x, window.innerWidth - 240);
  const safeY = Math.min(y, window.innerHeight - 300);

  return (
    <div 
      ref={menuRef}
      className="absolute z-50 w-56 bg-industrial-800 border border-industrial-700 shadow-[0_8px_24px_rgba(0,0,0,0.8)] rounded py-1 flex flex-col text-sm text-gray-300 font-sans"
      style={{ top: safeY, left: safeX }}
      onContextMenu={(e) => e.preventDefault()}
    >
      {(title || subtitle) && (
        <div className="px-3 py-2 border-b border-industrial-700/50 mb-1">
          {title && <div className="font-semibold text-gray-100 truncate">{title}</div>}
          {subtitle && <div className="text-[10px] font-mono text-gray-500 truncate mt-0.5">{subtitle}</div>}
        </div>
      )}
      
      {actions.map((act, i) => {
        if (act.separator) {
          return <div key={`sep-${i}`} className="h-px bg-industrial-700/50 my-1 mx-2" />;
        }
        return (
          <button
            key={i}
            disabled={act.disabled}
            onClick={() => {
              if (!act.disabled) {
                act.onClick();
                onClose();
              }
            }}
            className={`flex items-center w-full px-3 py-1.5 text-left transition-colors ${
              act.disabled ? 'opacity-30 cursor-not-allowed' :
              act.danger ? 'hover:bg-red-900/40 hover:text-red-400 text-red-400/80' : 
              'hover:bg-industrial-700 hover:text-white'
            }`}
          >
            {act.icon && <span className="mr-2 w-4 h-4 flex items-center justify-center opacity-70">{act.icon}</span>}
            <span className="flex-1 text-xs">{act.label}</span>
          </button>
        );
      })}
    </div>
  );
};

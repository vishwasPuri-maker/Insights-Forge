import React from 'react';
import { cn } from '@/lib/utils';

interface ConfidencePanelProps {
  score: number; // Domain score: 0.0 to 1.0
  label?: string;
  className?: string;
}

export const ConfidencePanel: React.FC<ConfidencePanelProps> = ({ score, label = "Confidence", className }) => {
  const percentage = Math.round(score * 100);
  
  const getColor = (val: number) => {
    if (val >= 80) return "bg-brand-success";
    if (val >= 50) return "bg-brand-warning";
    return "bg-brand-error";
  };

  return (
    <div className={cn("flex flex-col space-y-1.5", className)}>
      <div className="flex justify-between items-center text-caption font-medium">
        <span className="text-muted-foreground">{label}</span>
        <span className="text-foreground">{percentage}%</span>
      </div>
      <div 
        role="progressbar" 
        aria-valuenow={percentage} 
        aria-valuemin={0} 
        aria-valuemax={100} 
        aria-label={label}
        className="h-2 w-full bg-muted overflow-hidden rounded-full"
      >
        <div 
          className={cn("h-full transition-all duration-500", getColor(percentage))} 
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

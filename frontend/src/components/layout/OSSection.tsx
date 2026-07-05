import React from 'react';
import { cn } from '@/lib/utils';

interface OSSectionProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
}

export const OSSection: React.FC<OSSectionProps> = ({ title, description, children, className }) => {
  return (
    <section className={cn("flex flex-col gap-6", className)}>
      <div>
        <h2 className="text-h2 font-semibold tracking-tight">{title}</h2>
        {description && <p className="text-body text-muted-foreground mt-1">{description}</p>}
      </div>
      {children}
    </section>
  );
};

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import type { LucideIcon } from 'lucide-react';

interface KPIWidgetProps {
  title: string;
  value: string | number;
  icon?: LucideIcon;
  trend?: {
    value: number;
    label: string;
    direction: 'up' | 'down' | 'neutral';
  };
  className?: string;
}

export const KPIWidget: React.FC<KPIWidgetProps> = ({ title, value, icon: Icon, trend, className }) => {
  return (
    <Card className={cn("overflow-hidden border-border bg-card shadow-sm", className)}>
      <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
        <CardTitle className="text-h4 font-medium text-muted-foreground">
          {title}
        </CardTitle>
        {Icon && <Icon className="h-4 w-4 text-muted-foreground" />}
      </CardHeader>
      <CardContent>
        <div className="text-h2 font-bold text-foreground">{value}</div>
        {trend && (
          <div className="mt-2 flex items-center text-body">
            <Badge 
              variant="outline" 
              className={cn("mr-2 px-1 rounded-sm border-transparent", 
                trend.direction === 'up' ? "bg-brand-success/10 text-brand-success" :
                trend.direction === 'down' ? "bg-brand-error/10 text-brand-error" :
                "bg-muted text-muted-foreground"
              )}
            >
              {trend.direction === 'up' ? '+' : trend.direction === 'down' ? '-' : ''}
              {Math.abs(trend.value)}%
            </Badge>
            <span className="text-muted-foreground">{trend.label}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
